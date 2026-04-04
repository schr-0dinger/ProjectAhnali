# Optimization Backlog

Things we want to add eventually. None of this is enabled by default — every optimization needs to be gated behind a flag and backed by tests before it ships.

## Assets

**Images:**
- PNG → WebP/AVIF conversion
- Strip metadata (EXIF, ICC profiles)
- Remove unused alpha channels
- Downscale images that are bigger than they need to be
- Auto-generate density buckets (mdpi through xxxhdpi)
- Deduplicate identical images
- Nine-patch optimization
- SVG → VectorDrawable conversion
- Auto-generate mipmaps

**Video:**
- Re-encode oversized videos
- Downscale resolution, reduce bitrate
- Strip audio tracks from videos that don't need them

**Audio:**
- WAV → AAC/Opus
- Normalize volume, reduce bitrate
- Trim silence, strip metadata

## Resources

- Remove unused resources
- Inline small resource files
- Merge duplicate layouts
- Flatten deeply nested view hierarchies
- Detect and warn about deep nesting
- Optimize string tables, deduplicate repeated strings
- Auto-enable resource shrinking

## Code-level (DSL → Smali)

- Harden dead code elimination
- Remove unused functions and state variables
- Inline small functions
- Constant folding
- Branch pruning, unreachable code detection
- Merge identical event handlers

## Dependencies (AAR/JAR)

- Detect unused classes and methods
- Flag duplicate or conflicting library versions
- Warn about heavy transitive dependencies and suggest lighter alternatives

## Manifest

- Remove unused permissions
- Detect over-privileged configs
- Warn about exported components
- Merge duplicate intent filters
- Suggest minSdk/targetSdk adjustments

## Native layer (if/when we use it)

- Strip debug symbols from .so files
- Enable LTO
- Validate ABI completeness
- Check for architecture mismatches

## Performance static analysis

- Block network calls on main thread
- Flag expensive operations inside loops or UI callbacks
- Detect excessive state updates
- Warn about inefficient list binding patterns

## Security

- Detect hardcoded secrets
- Warn about insecure HTTP endpoints
- Flag weak crypto usage
- Strip debug logs in release builds
- Warn about exported services and unsafe file permissions

## Build-time

- Deterministic build hashing
- Reproducible artifacts
- Version stamping
- APK size diff reporting between builds
- Build-time benchmarking

## Architecture

- Detect circular navigation flows
- Find unreachable screens
- Flag state bloat
- Suggest better state scoping

## Packaging

- Auto-enable resource/code shrinking
- Optimize dex file ordering
- Multi-dex splitting when needed
- Generate minimal proguard rules

## Developer experience

- Lint for anti-patterns
- Suggest better DSL constructs
- Auto-format DSL code
- Detect complexity hotspots
- Visual UI tree map
- Build performance profiling reports
