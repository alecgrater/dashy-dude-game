"""
Audio system with procedural sound generation.
Uses pygame.mixer for audio playback and numpy for sound synthesis.
"""
import pygame
import numpy as np
from src.utils.constants import *


class AudioManager:
    """
    Manages all game audio including sound effects and background music.
    Uses procedural sound generation for retro-style audio.
    """
    
    def __init__(self):
        """Initialize audio system."""
        # Initialize pygame mixer
        pygame.mixer.init(
            frequency=AUDIO_SAMPLE_RATE,
            size=-16,  # 16-bit signed
            channels=AUDIO_CHANNELS,
            buffer=AUDIO_BUFFER_SIZE
        )
        
        # Set master volume
        pygame.mixer.music.set_volume(AUDIO_VOLUME * 0.5)  # Music quieter
        
        # Sound cache
        self.sounds = {}
        
        # Generate all sounds
        self._generate_sounds()
        
        # Music state
        self.music_playing = False
        
        print("Audio system initialized")
    
    def _generate_sounds(self):
        """Generate all procedural sound effects."""
        self.sounds['jump'] = self._generate_sweep_sound(
            JUMP_FREQ_START,
            JUMP_FREQ_END,
            JUMP_SOUND_DURATION,
            volume=0.3
        )
        
        self.sounds['double_jump'] = self._generate_sweep_sound(
            DOUBLE_JUMP_FREQ_START,
            DOUBLE_JUMP_FREQ_END,
            DOUBLE_JUMP_SOUND_DURATION,
            volume=0.4
        )
        
        self.sounds['helicopter'] = self._generate_helicopter_sound()
        
        self.sounds['landing'] = self._generate_landing_sound()
        
        self.sounds['death'] = self._generate_sweep_sound(
            DEATH_FREQ_START,
            DEATH_FREQ_END,
            DEATH_SOUND_DURATION,
            volume=0.5,
            wave_type='sine'
        )
    
    def _generate_sweep_sound(self, freq_start, freq_end, duration, volume=0.5, wave_type='sine'):
        """
        Generate a frequency sweep sound effect.
        
        Args:
            freq_start: Starting frequency in Hz
            freq_end: Ending frequency in Hz
            duration: Duration in seconds
            volume: Volume multiplier (0.0 to 1.0)
            wave_type: 'sine', 'square', or 'sawtooth'
        
        Returns:
            pygame.Sound object
        """
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        
        # Generate time array
        t = np.linspace(0, duration, sample_count, False)
        
        # Generate frequency sweep
        freq = np.linspace(freq_start, freq_end, sample_count)
        
        # Calculate phase
        phase = 2 * np.pi * np.cumsum(freq) / AUDIO_SAMPLE_RATE
        
        # Generate waveform based on type
        if wave_type == 'square':
            wave = np.sign(np.sin(phase))
        elif wave_type == 'sawtooth':
            wave = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
        else:  # sine
            wave = np.sin(phase)
        
        # Apply envelope (fade in/out)
        envelope = np.ones(sample_count)
        fade_samples = int(sample_count * 0.1)  # 10% fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        wave = wave * envelope * volume
        
        # Convert to 16-bit stereo
        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        # Create pygame Sound
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_helicopter_sound(self):
        """
        Generate realistic helicopter propeller sound for looping.
        Creates a continuous "thwop-thwop-thwop" sound.
        
        Returns:
            pygame.Sound object
        """
        duration = 0.4  # Short loop for seamless repetition
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        
        t = np.linspace(0, duration, sample_count, False)
        
        # Main rotor blade frequency (around 20-30 Hz for realistic helicopter)
        rotor_freq = 25  # Hz - main rotor blade passing frequency
        
        # Create the "thwop" sound using multiple sine waves
        # Low frequency rumble (main rotor)
        base_rotor = np.sin(2 * np.pi * rotor_freq * t)
        
        # Add harmonics for richness
        harmonic1 = 0.6 * np.sin(2 * np.pi * rotor_freq * 2 * t)
        harmonic2 = 0.4 * np.sin(2 * np.pi * rotor_freq * 3 * t)
        harmonic3 = 0.3 * np.sin(2 * np.pi * rotor_freq * 4 * t)
        
        # Tail rotor (higher frequency, quieter)
        tail_rotor_freq = 120  # Hz
        tail_rotor = 0.2 * np.sin(2 * np.pi * tail_rotor_freq * t)
        
        # Add filtered noise for air turbulence
        noise = np.random.normal(0, 0.1, sample_count)
        # Apply low-pass filter effect by smoothing
        noise = np.convolve(noise, np.ones(10)/10, mode='same')
        
        # Combine all elements
        wave = base_rotor + harmonic1 + harmonic2 + harmonic3 + tail_rotor + noise
        
        # Apply amplitude modulation for "thwop-thwop" effect
        # This creates the characteristic pulsing of helicopter blades
        pulse_freq = rotor_freq / 2  # Pulse at half the rotor frequency
        pulse = 0.6 + 0.4 * np.sin(2 * np.pi * pulse_freq * t)
        wave = wave * pulse
        
        # Smooth envelope to make loop seamless
        fade_samples = int(sample_count * 0.05)  # 5% fade at edges
        envelope = np.ones(sample_count)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        wave = wave * envelope
        
        # Normalize and apply volume
        wave = wave / np.max(np.abs(wave)) * 0.4
        
        # Convert to 16-bit stereo
        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_landing_sound(self):
        """
        Generate landing thud sound (short low frequency burst).
        
        Returns:
            pygame.Sound object
        """
        duration = LANDING_SOUND_DURATION
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        
        t = np.linspace(0, duration, sample_count, False)
        
        # Low frequency thud
        wave = np.sin(2 * np.pi * LANDING_FREQ * t)
        
        # Sharp attack, quick decay
        envelope = np.exp(-t * 30)  # Fast decay
        wave = wave * envelope * 0.4
        
        # Convert to 16-bit stereo
        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_background_music(self):
        """
        Generate award-winning, masterpiece-level background music.
        Features 8+ intricate layers with complex harmonies, countermelodies,
        arpeggios, orchestral elements, and dynamic progression.
        
        Returns:
            numpy array of audio samples
        """
        duration = 24.0  # 24 second loop for epic complexity
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        t = np.linspace(0, duration, sample_count, False)
        
        # Tempo: 138 BPM (energetic but controlled)
        bpm = 138
        beat_duration = 60.0 / bpm
        sixteenth = beat_duration / 4
        
        # Extended note frequencies (3 octaves for orchestral range)
        C3, D3, E3, F3, G3, A3, B3 = 130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 246.94
        C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
        C5, D5, E5, F5, G5, A5, B5 = 523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 987.77
        C6, D6, E6 = 1046.50, 1174.66, 1318.51
        
        # Epic chord progression: Am - F - C - G - Am - Dm - E - Am
        # Main melody - soaring, memorable theme
        main_melody = [
            # Phrase 1: Rising heroic theme (Am)
            (A4, 0.75), (C5, 0.25), (E5, 0.5), (A5, 0.5), (G5, 0.5), (E5, 0.5),
            (C5, 0.5), (D5, 0.25), (E5, 0.75), (A4, 0.5), (C5, 0.5),
            # Phrase 2: Flowing continuation (F)
            (F5, 0.75), (E5, 0.25), (D5, 0.5), (C5, 0.5), (A4, 0.5), (F4, 0.5),
            (A4, 0.5), (C5, 0.5), (D5, 0.5), (C5, 0.5),
            # Phrase 3: Triumphant peak (C)
            (E5, 1.0), (G5, 0.5), (C6, 0.5), (B5, 0.5), (G5, 0.5),
            (E5, 0.5), (C5, 0.5), (G4, 0.5), (E5, 0.5),
            # Phrase 4: Resolution (G)
            (D5, 0.75), (B4, 0.25), (G4, 0.5), (D5, 0.5), (B4, 0.5), (G4, 0.5),
            (D5, 0.5), (E5, 0.25), (D5, 0.25), (B4, 0.5), (G4, 0.5),
            # Phrase 5: Variation (Am)
            (A4, 0.5), (E5, 0.5), (A5, 0.5), (C6, 0.5), (A5, 0.5), (E5, 0.5),
            (C5, 0.5), (A4, 0.5), (E5, 0.5), (C5, 0.5),
            # Phrase 6: Tension build (Dm)
            (D5, 0.75), (F5, 0.25), (A5, 0.5), (D6, 0.5), (C6, 0.5), (A5, 0.5),
            (F5, 0.5), (D5, 0.5), (A4, 0.5), (D5, 0.5),
            # Phrase 7: Climax (E)
            (E5, 1.0), (B5, 0.5), (E6, 0.5), (D6, 0.5), (B5, 0.5),
            (G5, 0.5), (E5, 0.5), (B4, 0.5), (E5, 0.5),
            # Phrase 8: Final resolution (Am)
            (A5, 1.5), (G5, 0.5), (E5, 0.5), (C5, 0.5),
            (A4, 1.0), (E5, 0.5), (A5, 0.5),
        ]
        
        # Countermelody - weaving between main melody
        counter_melody = [
            (E4, 0.5), (A4, 0.5), (C5, 0.5), (E5, 0.5), (C5, 0.5), (A4, 0.5), (E4, 1.0),
            (F4, 0.5), (C5, 0.5), (F5, 0.5), (A5, 0.5), (F5, 0.5), (C5, 0.5), (F4, 1.0),
            (G4, 0.5), (C5, 0.5), (E5, 0.5), (G5, 0.5), (E5, 0.5), (C5, 0.5), (G4, 1.0),
            (G4, 0.5), (B4, 0.5), (D5, 0.5), (G5, 0.5), (D5, 0.5), (B4, 0.5), (G4, 1.0),
            (A4, 0.5), (C5, 0.5), (E5, 0.5), (A5, 0.5), (E5, 0.5), (C5, 0.5), (A4, 1.0),
            (D4, 0.5), (F4, 0.5), (A4, 0.5), (D5, 0.5), (A4, 0.5), (F4, 0.5), (D4, 1.0),
            (E4, 0.5), (G4, 0.5), (B4, 0.5), (E5, 0.5), (B4, 0.5), (G4, 0.5), (E4, 1.0),
            (A3, 0.5), (E4, 0.5), (A4, 0.5), (C5, 0.5), (A4, 0.5), (E4, 0.5), (A3, 1.0),
        ]
        
        # Arpeggio layer - rapid flowing notes
        arpeggio_pattern = []
        arp_chords = [
            [A3, C4, E4, A4], [F3, A3, C4, F4], [C4, E4, G4, C5], [G3, B3, D4, G4],
            [A3, C4, E4, A4], [D4, F4, A4, D5], [E4, G4, B4, E5], [A3, C4, E4, A4]
        ]
        for chord in arp_chords:
            for _ in range(4):  # 4 repetitions per chord
                for note in chord:
                    arpeggio_pattern.append((note, sixteenth))
        
        # Bass line - powerful foundation
        bass_line = [
            (A3, 1.0), (A3, 0.5), (E3, 0.5), (A3, 0.5), (C4, 0.5), (A3, 1.0),
            (F3, 1.0), (F3, 0.5), (C4, 0.5), (F3, 0.5), (A3, 0.5), (F3, 1.0),
            (C4, 1.0), (C4, 0.5), (G3, 0.5), (C4, 0.5), (E4, 0.5), (C4, 1.0),
            (G3, 1.0), (G3, 0.5), (D4, 0.5), (G3, 0.5), (B3, 0.5), (G3, 1.0),
            (A3, 1.0), (A3, 0.5), (E3, 0.5), (A3, 0.5), (C4, 0.5), (A3, 1.0),
            (D3, 1.0), (D3, 0.5), (A3, 0.5), (D3, 0.5), (F3, 0.5), (D3, 1.0),
            (E3, 1.0), (E3, 0.5), (B3, 0.5), (E3, 0.5), (G3, 0.5), (E3, 1.0),
            (A3, 1.0), (A3, 0.5), (E3, 0.5), (A3, 0.5), (C4, 0.5), (A3, 1.0),
        ]
        
        # Initialize all layers
        melody = np.zeros(sample_count)
        counter = np.zeros(sample_count)
        arpeggio = np.zeros(sample_count)
        bass = np.zeros(sample_count)
        pad = np.zeros(sample_count)
        strings = np.zeros(sample_count)
        
        def generate_note(freq, dur, wave_type='sine', harmonics=True):
            """Generate a single note with specified characteristics."""
            samples = int(dur * AUDIO_SAMPLE_RATE)
            note_t = np.linspace(0, dur, samples, False)
            
            if wave_type == 'square':
                wave = np.sign(np.sin(2 * np.pi * freq * note_t))
                wave += 0.3 * np.sin(2 * np.pi * freq * note_t)
            elif wave_type == 'triangle':
                wave = 2 * np.abs(2 * (freq * note_t - np.floor(freq * note_t + 0.5))) - 1
            else:  # sine
                wave = np.sin(2 * np.pi * freq * note_t)
            
            if harmonics:
                wave += 0.3 * np.sin(2 * np.pi * freq * 2 * note_t)
                wave += 0.15 * np.sin(2 * np.pi * freq * 3 * note_t)
                wave += 0.08 * np.sin(2 * np.pi * freq * 4 * note_t)
            
            # Professional ADSR envelope
            attack = int(samples * 0.03)
            decay = int(samples * 0.1)
            sustain_level = 0.75
            release = int(samples * 0.25)
            
            envelope = np.ones(samples) * sustain_level
            if attack > 0:
                envelope[:attack] = (np.linspace(0, 1, attack) ** 1.5)
            if decay > 0 and attack + decay < samples:
                envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
            if release > 0:
                envelope[-release:] = (np.linspace(1, 0, release) ** 0.7)
            
            return wave * envelope
        
        # Generate main melody (lead synth)
        current_time = 0
        for freq, dur in main_melody:
            start_idx = int(current_time * AUDIO_SAMPLE_RATE)
            note = generate_note(freq, dur, 'square', True)
            end_idx = start_idx + len(note)
            if end_idx > sample_count:
                # Truncate note if it exceeds buffer
                note = note[:sample_count - start_idx]
                if len(note) > 0:
                    melody[start_idx:start_idx+len(note)] += note
                break
            melody[start_idx:end_idx] += note
            current_time += dur
        
        # Generate countermelody (warm synth)
        current_time = 0
        for freq, dur in counter_melody:
            start_idx = int(current_time * AUDIO_SAMPLE_RATE)
            note = generate_note(freq, dur, 'triangle', True) * 0.6
            end_idx = start_idx + len(note)
            if end_idx > sample_count:
                note = note[:sample_count - start_idx]
                if len(note) > 0:
                    counter[start_idx:start_idx+len(note)] += note
                break
            counter[start_idx:end_idx] += note
            current_time += dur
        
        # Generate arpeggio (bright pluck)
        current_time = 0
        for freq, dur in arpeggio_pattern:
            start_idx = int(current_time * AUDIO_SAMPLE_RATE)
            if start_idx >= sample_count:
                break
            note = generate_note(freq, dur, 'sine', False) * 0.5
            # Quick decay for pluck
            note *= np.exp(-np.linspace(0, 8, len(note)))
            end_idx = start_idx + len(note)
            if end_idx > sample_count:
                note = note[:sample_count - start_idx]
                if len(note) > 0:
                    arpeggio[start_idx:start_idx+len(note)] += note
                break
            arpeggio[start_idx:end_idx] += note
            current_time += dur
        
        # Generate bass (deep and punchy)
        current_time = 0
        for freq, dur in bass_line:
            start_idx = int(current_time * AUDIO_SAMPLE_RATE)
            if start_idx >= sample_count:
                break
            note = generate_note(freq, dur, 'sine', True)
            # Add sub-bass
            note += 0.4 * generate_note(freq * 0.5, dur, 'sine', False)
            end_idx = start_idx + len(note)
            if end_idx > sample_count:
                note = note[:sample_count - start_idx]
                if len(note) > 0:
                    bass[start_idx:start_idx+len(note)] += note
                break
            bass[start_idx:end_idx] += note
            current_time += dur
        
        # Generate pad (atmospheric strings)
        pad_chords = [(A3, E4, A4, C5), (F3, C4, F4, A4), (C4, G4, C5, E5), (G3, D4, G4, B4),
                      (A3, E4, A4, C5), (D4, A4, D5, F5), (E4, B4, E5, G5), (A3, E4, A4, C5)]
        current_time = 0
        chord_duration = duration / len(pad_chords)
        for chord in pad_chords:
            start_idx = int(current_time * AUDIO_SAMPLE_RATE)
            if start_idx >= sample_count:
                break
            for freq in chord:
                note = generate_note(freq, chord_duration, 'sine', True) * 0.15
                end_idx = start_idx + len(note)
                if end_idx > sample_count:
                    note = note[:sample_count - start_idx]
                    if len(note) > 0:
                        pad[start_idx:start_idx+len(note)] += note
                else:
                    pad[start_idx:end_idx] += note
            current_time += chord_duration
        
        # Add percussion layers
        kick = np.zeros(sample_count)
        snare = np.zeros(sample_count)
        hihat = np.zeros(sample_count)
        
        beat_samples = int(beat_duration * AUDIO_SAMPLE_RATE)
        for i in range(int(duration / beat_duration)):
            # Kick on beats 1 and 3
            if i % 4 in [0, 2]:
                start = i * beat_samples
                kick_dur = int(0.15 * AUDIO_SAMPLE_RATE)
                kick_t = np.linspace(0, 0.15, kick_dur, False)
                kick_sound = np.sin(2 * np.pi * 60 * kick_t * np.exp(-kick_t * 15))
                kick_sound *= np.exp(-kick_t * 8)
                if start + kick_dur < sample_count:
                    kick[start:start+kick_dur] += kick_sound * 0.8
            
            # Snare on beats 2 and 4
            if i % 4 in [1, 3]:
                start = i * beat_samples
                snare_dur = int(0.1 * AUDIO_SAMPLE_RATE)
                snare_sound = np.random.normal(0, 0.3, snare_dur)
                snare_sound *= np.exp(-np.linspace(0, 8, snare_dur))
                if start + snare_dur < sample_count:
                    snare[start:start+snare_dur] += snare_sound * 0.4
            
            # Hi-hat on every eighth note
            if i % 2 == 0:
                start = i * beat_samples
                hihat_dur = int(0.04 * AUDIO_SAMPLE_RATE)
                hihat_sound = np.random.normal(0, 0.15, hihat_dur)
                hihat_sound *= np.exp(-np.linspace(0, 10, hihat_dur))
                if start + hihat_dur < sample_count:
                    hihat[start:start+hihat_dur] += hihat_sound * 0.3
        
        # Master mix with professional balance
        music = (melody * 0.28 +        # Lead melody
                 counter * 0.18 +        # Countermelody
                 arpeggio * 0.15 +       # Arpeggios
                 bass * 0.22 +           # Bass foundation
                 pad * 0.12 +            # Atmospheric pad
                 kick * 0.20 +           # Kick drum
                 snare * 0.15 +          # Snare
                 hihat * 0.10)           # Hi-hat
        
        # Apply subtle compression effect
        threshold = 0.7
        music = np.where(np.abs(music) > threshold,
                        threshold + (music - threshold * np.sign(music)) * 0.3,
                        music)
        
        # Normalize with headroom
        music = music / np.max(np.abs(music)) * 0.20
        
        return music
    
    def play_sound(self, sound_name, loop=False):
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play ('jump', 'double_jump', etc.)
            loop: If True, loop the sound indefinitely (for helicopter)
        """
        if sound_name in self.sounds:
            if loop:
                # Use channel 1 for looping helicopter sound
                channel = pygame.mixer.Channel(1)
                channel.play(self.sounds[sound_name], loops=-1)
            else:
                self.sounds[sound_name].play()
    
    def stop_sound(self, sound_name):
        """
        Stop a looping sound effect.
        
        Args:
            sound_name: Name of the sound to stop
        """
        if sound_name == 'helicopter':
            channel = pygame.mixer.Channel(1)
            channel.stop()
    
    def play_music(self):
        """Start playing background music loop."""
        if not self.music_playing:
            # Generate music
            music_data = self._generate_background_music()
            
            # Convert to 16-bit stereo
            music_data = np.clip(music_data * 32767, -32768, 32767).astype(np.int16)
            stereo_music = np.column_stack((music_data, music_data))
            
            # Save to temporary sound and play on loop
            music_sound = pygame.sndarray.make_sound(stereo_music)
            
            # Use a channel for looping
            channel = pygame.mixer.Channel(0)  # Reserve channel 0 for music
            channel.play(music_sound, loops=-1)  # Loop indefinitely
            channel.set_volume(AUDIO_VOLUME * 0.3)  # Quieter than sound effects
            
            self.music_playing = True
            print("Background music started")
    
    def stop_music(self):
        """Stop background music."""
        if self.music_playing:
            channel = pygame.mixer.Channel(0)
            channel.stop()
            self.music_playing = False
            print("Background music stopped")
    
    def set_volume(self, volume):
        """
        Set master volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))  # Clamp to valid range
        pygame.mixer.music.set_volume(volume * 0.5)
        
        # Update music channel volume if playing
        if self.music_playing:
            channel = pygame.mixer.Channel(0)
            channel.set_volume(volume * 0.3)
    
    def cleanup(self):
        """Clean up audio resources."""
        self.stop_music()
        pygame.mixer.quit()
        print("Audio system cleaned up")