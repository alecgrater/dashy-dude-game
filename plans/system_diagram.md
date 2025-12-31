# System Architecture Diagram

## High-Level Game Flow

```mermaid
graph TD
    A[Game Start] --> B[Initialize Pygame]
    B --> C[Load Assets]
    C --> D[Title State]
    D --> E{User Clicks Play?}
    E -->|No| D
    E -->|Yes| F[Play State]
    F --> G[Game Loop]
    G --> H{Player Alive?}
    H -->|Yes| G
    H -->|No| I[Game Over State]
    I --> J{Restart?}
    J -->|Yes| F
    J -->|No| D
```

## Core Game Loop Architecture

```mermaid
graph LR
    A[Main Loop 60 FPS] --> B[Handle Input]
    B --> C[Update Physics]
    C --> D[Update Entities]
    D --> E[Update Camera]
    E --> F[Check Collisions]
    F --> G[Update Difficulty]
    G --> H[Render Scene]
    H --> I[Render UI]
    I --> A
```

## Player State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running: Move Input
    Running --> Idle: Stop Moving
    Running --> Jumping: Space Press
    Idle --> Jumping: Space Press
    Jumping --> DoubleJumping: Space Press
    DoubleJumping --> Helicopter: Hold Space
    Helicopter --> Falling: Duration End
    Jumping --> Falling: Peak Reached
    DoubleJumping --> Falling: Peak Reached
    Falling --> Running: Land on Platform
    Falling --> Dead: Hit Water
    Dead --> [*]
```

## Entity Relationship Diagram

```mermaid
classDiagram
    Game --> StateManager
    StateManager --> TitleState
    StateManager --> PlayState
    StateManager --> GameOverState
    
    PlayState --> Player
    PlayState --> PlatformGenerator
    PlayState --> Camera
    PlayState --> AudioManager
    PlayState --> UIRenderer
    
    Player --> PhysicsEngine
    Player --> AnimationSystem
    Player --> InputHandler
    
    PlatformGenerator --> Platform
    Platform --> PhysicsEngine
    
    Camera --> Player
    Camera --> ParallaxBackground
    
    class Game {
        +screen: Surface
        +clock: Clock
        +state_manager: StateManager
        +run()
    }
    
    class Player {
        +position: Vector2
        +velocity: Vector2
        +state: PlayerState
        +jump_count: int
        +helicopter_time: float
        +update(dt)
        +jump()
        +double_jump()
        +activate_helicopter()
    }
    
    class Platform {
        +position: Vector2
        +width: int
        +height: int
        +type: PlatformType
        +is_moving: bool
        +update(dt)
    }
    
    class PhysicsEngine {
        +gravity: float
        +apply_gravity(entity, dt)
        +check_collision(entity, platforms)
        +resolve_collision(entity, platform)
    }
```

## Data Flow: Jump Mechanics

```mermaid
sequenceDiagram
    participant Input
    participant Player
    participant Physics
    participant Animation
    participant Audio
    
    Input->>Player: Space Key Press
    Player->>Player: Check Jump Count
    
    alt First Jump
        Player->>Physics: Apply Jump Velocity
        Player->>Animation: Play Jump Animation
        Player->>Audio: Play Jump Sound
        Player->>Player: Increment Jump Count
    else Second Jump
        Player->>Physics: Apply Double Jump Velocity
        Player->>Animation: Play Double Jump Animation
        Player->>Audio: Play Double Jump Sound
        Player->>Player: Increment Jump Count
    else Helicopter (Hold Space)
        Player->>Physics: Reduce Fall Speed
        Player->>Animation: Play Helicopter Animation
        Player->>Audio: Play Helicopter Sound Loop
        Player->>Player: Start Helicopter Timer
    end
```

## Platform Generation System

```mermaid
flowchart TD
    A[Check Camera Position] --> B{Need New Platform?}
    B -->|No| A
    B -->|Yes| C[Calculate Next Position]
    C --> D[Get Difficulty Level]
    D --> E[Determine Platform Type]
    E --> F{Type?}
    F -->|Static| G[Create Static Platform]
    F -->|Moving| H[Create Moving Platform]
    F -->|Small| I[Create Small Platform]
    F -->|Crumbling| J[Create Crumbling Platform]
    G --> K[Add to Platform Pool]
    H --> K
    I --> K
    J --> K
    K --> L[Position Platform]
    L --> A
```

## Rendering Pipeline

```mermaid
graph TB
    A[Start Render] --> B[Clear Screen]
    B --> C[Render Sky Gradient]
    C --> D[Render Far Parallax Layer]
    D --> E[Render Mid Parallax Layer]
    E --> F[Render Water Surface]
    F --> G[Apply Camera Transform]
    G --> H[Render Platforms]
    H --> I[Render Player]
    I --> J[Render Particles]
    J --> K[Render Near Parallax Layer]
    K --> L[Reset Camera Transform]
    L --> M[Render UI Elements]
    M --> N[Apply Screen Shake]
    N --> O[Flip Display]
    O --> P[End Render]
```

## Collision Detection Flow

```mermaid
flowchart LR
    A[Player Update] --> B[Update Position]
    B --> C[Get Nearby Platforms]
    C --> D{Check Each Platform}
    D --> E{AABB Collision?}
    E -->|No| D
    E -->|Yes| F{Player Falling?}
    F -->|No| D
    F -->|Yes| G[Resolve Collision]
    G --> H[Set Player on Platform]
    H --> I[Reset Jump Count]
    I --> J[Play Landing Sound]
    J --> K[Create Landing Particles]
    K --> L[Trigger Landing Animation]
```

## Audio System Architecture

```mermaid
graph TD
    A[Audio Manager] --> B[Sound Generator]
    A --> C[Music Generator]
    A --> D[Sound Pool]
    
    B --> E[Generate Jump Sound]
    B --> F[Generate Double Jump Sound]
    B --> G[Generate Helicopter Sound]
    B --> H[Generate Landing Sound]
    B --> I[Generate Death Sound]
    
    C --> J[Generate Background Loop]
    C --> K[Generate Layer 1]
    C --> L[Generate Layer 2]
    C --> M[Generate Layer 3]
    
    D --> N[Cache Generated Sounds]
    D --> O[Manage Playback]
    D --> P[Control Volume]
```

## Performance Optimization Strategy

```mermaid
mindmap
  root((Performance))
    Rendering
      Sprite Caching
      Dirty Rectangles
      Culling Off-Screen
      Batch Drawing
    Updates
      Object Pooling
      Spatial Partitioning
      Lazy Evaluation
      Fixed Timestep
    Memory
      Asset Preloading
      Sound Caching
      Platform Pool Limit
      Particle Pool Limit
    Profiling
      FPS Counter
      Draw Call Count
      Update Time
      Memory Usage
```

## Difficulty Progression System

```mermaid
graph LR
    A[Game Time] --> B{Every 10 Seconds}
    B --> C[Increase Game Speed]
    C --> D[Widen Platform Gaps]
    D --> E[Increase Moving Platforms]
    E --> F{Time > 30s?}
    F -->|Yes| G[Add Crumbling Platforms]
    F -->|No| H[Continue]
    G --> H
    H --> I{Time > 60s?}
    I -->|Yes| J[Max Difficulty]
    I -->|No| B
```

## Input Handling System

```mermaid
sequenceDiagram
    participant Event
    participant InputHandler
    participant InputBuffer
    participant Player
    
    Event->>InputHandler: Key Press
    InputHandler->>InputBuffer: Store Input with Timestamp
    
    loop Every Frame
        Player->>InputBuffer: Check for Buffered Input
        InputBuffer->>InputBuffer: Remove Expired Inputs
        InputBuffer->>Player: Return Valid Input
        Player->>Player: Process Input
    end
    
    Note over InputBuffer: Buffer Duration: 150ms
    Note over Player: Coyote Time: 100ms
```

## Camera Smoothing Algorithm

```mermaid
flowchart TD
    A[Get Player Position] --> B[Calculate Desired Camera Position]
    B --> C[Apply Horizontal Offset]
    C --> D[Check Vertical Bounds]
    D --> E[Apply Lerp Smoothing]
    E --> F{Screen Shake Active?}
    F -->|Yes| G[Add Shake Offset]
    F -->|No| H[Update Camera Position]
    G --> H
    H --> I[Clamp to World Bounds]
    I --> J[Return Camera Transform]
```

## Asset Generation Pipeline

```mermaid
graph TB
    A[Game Initialization] --> B[Generate Player Sprites]
    B --> C[Generate Platform Sprites]
    C --> D[Generate Particle Sprites]
    D --> E[Generate UI Elements]
    E --> F[Generate Background Layers]
    F --> G[Cache All Surfaces]
    G --> H[Generate Audio Samples]
    H --> I[Ready to Play]
    
    B --> B1[Idle Frames]
    B --> B2[Run Frames]
    B --> B3[Jump Frames]
    B --> B4[Double Jump Frames]
    B --> B5[Helicopter Frames]
    
    C --> C1[Static Platform]
    C --> C2[Moving Platform]
    C --> C3[Small Platform]
    C --> C4[Crumbling Platform]
```

## Memory Management Strategy

```mermaid
graph LR
    A[Object Pool] --> B[Platform Pool]
    A --> C[Particle Pool]
    A --> D[Sound Pool]
    
    B --> E[Max 20 Platforms]
    C --> F[Max 50 Particles]
    D --> G[Max 10 Concurrent Sounds]
    
    E --> H[Reuse Inactive]
    F --> H
    G --> H
    
    H --> I[Reset Properties]
    I --> J[Return to Pool]
```

This diagram set provides a comprehensive visual overview of the game's architecture, showing how different systems interact and data flows through the application.