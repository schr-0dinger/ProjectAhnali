# Ahnali Optimization Backlog (Future Plan)

Status: Planned backlog (not implemented by default)
Scope: Build-time optimization, static analysis, packaging intelligence, and architecture hygiene.

## 1) Asset Optimization

### Images
- [ ] PNG -> WebP (lossy/lossless)
- [ ] PNG -> AVIF
- [ ] Auto strip metadata (EXIF, ICC profiles)
- [ ] Remove unused alpha channel
- [ ] Downscale oversized images
- [ ] Auto-generate density buckets (mdpi -> xxxhdpi)
- [ ] Deduplicate identical images
- [ ] Detect unused images
- [ ] Optimize nine-patch images
- [ ] Convert SVG -> VectorDrawable
- [ ] Auto-generate mipmaps

### Video
- [ ] Re-encode large videos
- [ ] Downscale resolution
- [ ] Reduce bitrate
- [ ] Convert to efficient codec
- [ ] Remove audio if unused

### Audio
- [ ] Convert WAV -> AAC/Opus
- [ ] Normalize volume
- [ ] Reduce bitrate
- [ ] Trim silence
- [ ] Strip metadata

## 2) Resource Optimization

- [ ] Remove unused resources
- [ ] Inline small resources
- [ ] Merge duplicate layouts
- [ ] Flatten nested layout hierarchies
- [ ] Detect deep view nesting
- [ ] Suggest constraint optimizations
- [ ] Optimize string tables
- [ ] Deduplicate repeated strings
- [ ] Auto-enable resource shrinking flags

## 3) Code-Level Optimization (DSL -> Smali)

- [ ] Dead code elimination hardening
- [ ] Remove unused functions
- [ ] Remove unused state variables
- [ ] Inline small functions
- [ ] Constant folding expansion
- [ ] Branch pruning
- [ ] Unreachable code detection
- [ ] Detect redundant recomposition triggers
- [ ] Optimize state diff checks
- [ ] Merge identical event handlers

## 4) Dependency Optimization (AAR/JAR)

- [ ] Detect unused classes
- [ ] Remove unused methods
- [ ] Detect duplicate libraries
- [ ] Warn about conflicting versions
- [ ] Shrink dependency graph
- [ ] Detect heavy transitive dependencies
- [ ] Suggest lighter alternatives

## 5) Manifest Optimization

- [ ] Remove unused permissions
- [ ] Detect over-privileged configuration
- [ ] Auto-remove redundant features
- [ ] Optimize minSdk/targetSdk hints
- [ ] Detect missing required permissions
- [ ] Merge duplicate intent filters
- [ ] Warn about exported components

## 6) Native Layer Optimization (If Used)

- [ ] Strip debug symbols from `.so`
- [ ] Enable LTO
- [ ] Remove unused exported symbols
- [ ] Validate ABI completeness
- [ ] Detect unsafe panics
- [ ] Optimize compilation flags
- [ ] Compress native libraries
- [ ] Check for architecture mismatches

## 7) Performance Static Analysis

- [ ] Detect blocking network calls on main thread
- [ ] Detect large object allocations in loops
- [ ] Detect repeated expensive calls in UI cycle
- [ ] Detect excessive state updates
- [ ] Detect inefficient list binding patterns
- [ ] Warn about heavy work inside UI callbacks
- [ ] Detect missing background dispatch

## 8) Security Optimization

- [ ] Detect hardcoded secrets
- [ ] Warn about insecure HTTP
- [ ] Check weak crypto usage
- [ ] Scan for debug flags left enabled
- [ ] Strip debug logs in release builds
- [ ] Detect unsafe file permissions
- [ ] Warn about exported services

## 9) Build-Time Enhancements

- [ ] Deterministic build hashing
- [ ] Reproducible build artifacts
- [ ] Asset fingerprinting
- [ ] Version stamping
- [ ] Auto semantic version increment
- [ ] Auto changelog generation
- [ ] APK size diff reporting
- [ ] Build-time benchmarking

## 10) App Architecture Optimization

- [ ] Detect circular navigation flows
- [ ] Detect unreachable screens
- [ ] Detect duplicate navigation routes
- [ ] Detect state bloat
- [ ] Suggest state scoping improvements
- [ ] Validate event handler consistency

## 11) Packaging Optimization

- [ ] Enable resource shrinking automatically
- [ ] Enable code shrinking rules
- [ ] Compress dex files
- [ ] Optimize class ordering
- [ ] Multi-dex splitting if needed
- [ ] Generate minimal proguard config

## 12) Developer Experience Enhancements

- [ ] Lint for anti-patterns
- [ ] Suggest better DSL constructs
- [ ] Auto-format DSL
- [ ] Enforce style guidelines
- [ ] Detect complexity hotspots
- [ ] Generate visual UI tree map
- [ ] Build performance profiling report
