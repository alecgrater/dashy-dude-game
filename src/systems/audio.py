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
        
        self.sounds['revive'] = self._generate_revive_sound()
        
        # Load speed boost sound from file
        self.sounds['speed_boost'] = pygame.mixer.Sound('assets/sounds/speed_boost.wav')
        self.sounds['speed_boost'].set_volume(0.10)  # Play at 10% volume
        print("Loaded speed boost sound from assets/sounds/speed_boost.wav")
        
        # Load base multiplier sound from file
        self.sounds['multiplier_base'] = pygame.mixer.Sound('assets/sounds/multiplier.wav')
        print("Loaded multiplier sound from assets/sounds/multiplier.wav")
        
        # Generate combo timeout sound (sad/deflating sound)
        self.sounds['combo_timeout'] = self._generate_combo_timeout_sound()
    
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
    
    def _generate_revive_sound(self):
        """
        Generate magical revive/respawn sound effect.
        Creates an uplifting, ethereal sound with ascending tones and sparkle.
        
        Returns:
            pygame.Sound object
        """
        duration = 0.8  # Longer for dramatic effect
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        
        t = np.linspace(0, duration, sample_count, False)
        
        # Main ascending sweep (magical whoosh)
        freq_start = 200
        freq_end = 1200
        freq = np.linspace(freq_start, freq_end, sample_count)
        phase = 2 * np.pi * np.cumsum(freq) / AUDIO_SAMPLE_RATE
        
        # Primary tone with harmonics
        wave = np.sin(phase)
        wave += 0.5 * np.sin(phase * 2)  # Octave harmonic
        wave += 0.3 * np.sin(phase * 3)  # Fifth harmonic
        
        # Add shimmer/sparkle effect (high frequency modulation)
        shimmer_freq = 8  # Hz - shimmer rate
        shimmer = 1.0 + 0.3 * np.sin(2 * np.pi * shimmer_freq * t)
        wave = wave * shimmer
        
        # Add bell-like tones for magical quality
        bell_freqs = [800, 1000, 1200, 1500]
        for bell_freq in bell_freqs:
            bell_t_offset = np.random.uniform(0, 0.1)  # Slight timing variation
            bell_phase = 2 * np.pi * bell_freq * (t - bell_t_offset)
            bell_wave = np.sin(bell_phase) * np.exp(-(t - bell_t_offset) * 4)
            bell_wave = np.where(t >= bell_t_offset, bell_wave, 0)
            wave += bell_wave * 0.2
        
        # Add ethereal pad (sustained background tone)
        pad_freq = 400
        pad = 0.3 * np.sin(2 * np.pi * pad_freq * t)
        pad += 0.2 * np.sin(2 * np.pi * pad_freq * 1.5 * t)
        wave += pad
        
        # Apply envelope (quick attack, sustained, gentle release)
        attack_samples = int(sample_count * 0.05)  # Quick attack
        release_samples = int(sample_count * 0.3)  # Gentle fade out
        
        envelope = np.ones(sample_count)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples) ** 0.5
        if release_samples > 0:
            envelope[-release_samples:] = (np.linspace(1, 0, release_samples) ** 2)
        
        wave = wave * envelope
        
        # Normalize and apply volume
        wave = wave / np.max(np.abs(wave)) * 0.5
        
        # Convert to 16-bit stereo
        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_combo_timeout_sound(self):
        """
        Generate a quick "fizzle out" sound for when combo times out.
        Distinctly different from death sound - more like air escaping or sparkles fading.
        
        Returns:
            pygame.Sound object
        """
        duration = 0.25  # Shorter than death sound
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        t = np.linspace(0, duration, sample_count, False)
        
        # High-pitched fizzle (very different from death's low sweep)
        # Multiple high frequencies that fade out like sparkles
        wave = np.zeros(sample_count)
        
        # Sparkle/fizzle frequencies (high pitched, shimmery)
        fizzle_freqs = [1800, 2200, 2600, 3000]
        for i, freq in enumerate(fizzle_freqs):
            # Each frequency starts at slightly different time
            delay = i * 0.02
            delay_samples = int(delay * AUDIO_SAMPLE_RATE)
            
            # Create descending shimmer
            freq_sweep = np.linspace(freq, freq * 0.6, sample_count)
            phase = 2 * np.pi * np.cumsum(freq_sweep) / AUDIO_SAMPLE_RATE
            
            tone = np.sin(phase) * 0.25
            # Quick decay for each sparkle
            tone *= np.exp(-t * (12 + i * 2))
            
            # Apply delay
            if delay_samples > 0 and delay_samples < sample_count:
                tone[:delay_samples] = 0
            
            wave += tone
        
        # Add subtle filtered noise for "air escaping" quality
        noise = np.random.normal(0, 0.15, sample_count)
        # High-pass effect by subtracting smoothed version
        smoothed = np.convolve(noise, np.ones(20)/20, mode='same')
        noise = noise - smoothed * 0.8
        noise *= np.exp(-t * 15)  # Quick decay
        wave += noise * 0.3
        
        # Add a subtle mid-tone "poof"
        poof_freq = 600
        poof = np.sin(2 * np.pi * poof_freq * t) * np.exp(-t * 20)
        wave += poof * 0.2
        
        # Apply overall envelope
        envelope = np.exp(-t * 8)  # Smooth decay
        wave = wave * envelope
        
        # Normalize and apply volume
        wave = wave / np.max(np.abs(wave)) * 0.3
        
        # Convert to 16-bit stereo
        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def play_sound(self, sound_name, loop=False):
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play ('jump', 'double_jump', etc.)
            loop: If True, loop the sound indefinitely (for helicopter, speed_boost)
        """
        if sound_name in self.sounds:
            if loop:
                # Use channel 1 for looping helicopter sound
                # Use channel 2 for looping speed boost sound
                if sound_name == 'helicopter':
                    channel = pygame.mixer.Channel(1)
                elif sound_name == 'speed_boost':
                    channel = pygame.mixer.Channel(2)
                else:
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
        elif sound_name == 'speed_boost':
            channel = pygame.mixer.Channel(2)
            channel.stop()
    
    def play_multiplier_sound(self, multiplier):
        """
        Play the multiplier sound with pitch shifting based on multiplier level.
        Higher multipliers = higher pitch for excitement.
        
        Args:
            multiplier: The multiplier level (2, 3, 4, 5, etc.)
        """
        if 'multiplier_base' in self.sounds:
            # Get the base sound
            base_sound = self.sounds['multiplier_base']
            
            # Calculate pitch shift based on multiplier
            # Start at normal pitch for x2, increase by ~12% per level (roughly 2 semitones)
            pitch_multiplier = 1.0 + (multiplier - 2) * 0.12
            
            # Get the sound array
            sound_array = pygame.sndarray.array(base_sound)
            
            # Resample to change pitch (smaller array = higher pitch)
            new_length = int(len(sound_array) / pitch_multiplier)
            
            # Use numpy interpolation to resample
            indices = np.linspace(0, len(sound_array) - 1, new_length)
            
            # Interpolate for each channel
            if len(sound_array.shape) == 2:  # Stereo
                resampled = np.zeros((new_length, sound_array.shape[1]), dtype=sound_array.dtype)
                for channel in range(sound_array.shape[1]):
                    resampled[:, channel] = np.interp(indices, np.arange(len(sound_array)), sound_array[:, channel])
            else:  # Mono
                resampled = np.interp(indices, np.arange(len(sound_array)), sound_array)
            
            # Create and play the pitch-shifted sound with reduced volume
            pitched_sound = pygame.sndarray.make_sound(resampled.astype(np.int16))
            pitched_sound.set_volume(0.4)  # Play at 40% volume
            pitched_sound.play()
    
    def play_music(self):
        """Start playing background music loop."""
        if not self.music_playing:
            # Load custom music file
            music_sound = pygame.mixer.Sound('assets/sounds/song_1.wav')
            print("Loaded custom background music from assets/sounds/song_1.wav")
            
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
    
    def pause_music(self):
        """Pause background music."""
        if self.music_playing:
            channel = pygame.mixer.Channel(0)
            channel.pause()
            print("Background music paused")
    
    def resume_music(self):
        """Resume background music."""
        if self.music_playing:
            channel = pygame.mixer.Channel(0)
            channel.unpause()
            print("Background music resumed")
    
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