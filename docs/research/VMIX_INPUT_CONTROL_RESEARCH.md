# vMix Input Control & Switching Research Report
## Session 3 Master Integration Sprint

**Research Date**: November 12, 2025  
**Platform**: vMix Live Streaming Software  
**Focus**: Input control, switching, effects, and layer management via API

---

## Executive Summary

vMix provides comprehensive API-based input control through both HTTP Web API and TCP API protocols. The system supports advanced input switching, real-time effects processing, multi-layer mixing, and sophisticated input property management. This report documents all major capabilities and implementation methods.

---

## 1. INPUT SWITCHING

### 1.1 Core Switching Mechanism

vMix supports hard cuts and transitions between inputs through the HTTP Web API and TCP API protocols.

#### Base URL Structure
```
http://127.0.0.1:8088/API/?Function=[FunctionName]&Input=[InputReference]
```

#### Default Port
- HTTP Web API: Port 8088
- TCP API: Alternative for lower processing overhead (embedded devices)

### 1.2 Input Reference Methods

Inputs can be specified in three ways:

#### 1. Input Number Reference
- **Range**: 1 to n (number of inputs in project)
- **Preview**: 0 (preview channel)
- **Active Input**: -1 (currently active input)

**Example**:
```
http://127.0.0.1:8088/API/?Function=CutDirect&Input=4
```

#### 2. Input Name Reference
- Case-sensitive
- Requires full title name including spaces
- Must exactly match input name in vMix

**Example**:
```
http://127.0.0.1:8088/API/?Function=Fade&Duration=1000&Input=Camera+1
```

#### 3. GUID Reference
- Universally Unique Identifier
- Found in XML "Key" attribute
- Provides exact input targeting across project saves

**Example**:
```
http://127.0.0.1:8088/API/?Function=Fade&Duration=1000&Input=877bb3e7-58bd-46a1-85ce-0d673aec6bf5
```

### 1.3 Switching Commands

#### Hard Cut Commands

| Function | Description | Parameters | Example |
|----------|-------------|-----------|---------|
| **CutDirect** | Immediate hard cut to input | Input | `?Function=CutDirect&Input=4` |
| **Cut** | Hard cut to specified input | Input | `?Function=Cut&Input=2` |

#### Transition Commands

| Function | Description | Parameters | Example |
|----------|-------------|-----------|---------|
| **Fade** | Fade transition to input | Input, Duration (ms) | `?Function=Fade&Duration=1000&Input=5` |
| **Slide** | Slide transition to input | Input, Duration (ms) | `?Function=Slide&Duration=500&Input=3` |
| **Push** | Push transition to input | Input, Duration (ms) | `?Function=Push&Duration=750&Input=2` |
| **Zoom** | Zoom transition to input | Input, Duration (ms) | `?Function=Zoom&Duration=1200&Input=6` |

#### Duration Parameter
- **Unit**: Milliseconds
- **Range**: 500-5000ms typical
- **Default**: Varies by transition type

#### Active Input Control

| Function | Description | Example |
|----------|-------------|---------|
| **ActiveInput** | Set input as currently active | `?Function=ActiveInput&Input=3` |
| **PreviewInput** | Preview input without going live | `?Function=PreviewInput&Input=4` |

### 1.4 API Response Codes

- **Success**: HTTP 200 OK
- **Error**: HTTP 500 Server Error
- **Blank Parameters**: Returns XML state information

---

## 2. INPUT EFFECTS & COLOR CORRECTION

### 2.1 Effects Capabilities

vMix processes effects in real-time using 4:4:4 32-bit color space for optimal video quality.

#### Available Effects

1. **Color Correction** - Professional color grading
2. **Deinterlacing** - Motion video optimization
3. **Sharpening** - Image detail enhancement
4. **Zoom** - Real-time zoom control
5. **Rotate** - Image rotation
6. **Pan** - Pan positioning
7. **Crop** - Input cropping/masking
8. **Custom Effects** - Effects stacking

### 2.2 Color Correction Parameters

Color correction values available for professional color grading:

| Parameter | Range | Effect |
|-----------|-------|--------|
| **Gamma** | Variable | Tonal midpoint adjustment |
| **Lift** | Variable | Shadow/black level adjustment |
| **Gain** | Variable | Highlight/white level adjustment |
| **Hue** | 0-360° | Color shift |
| **Saturation** | 0-100% | Color intensity |

#### Color Correction UI Access
- Available on all video inputs (cameras, videos, images)
- Located in input properties/effects panel
- Applied in real-time during production

### 2.3 Zoom & Pan Control

#### Zoom Parameters
- **Zoom X**: Horizontal zoom factor
- **Zoom Y**: Vertical zoom factor
- **Pan X**: Horizontal pan position
- **Pan Y**: Vertical pan position

#### API Control
Zoom and pan values are queryable via XML API and displayable for each input layer.

**API Query**:
```
http://127.0.0.1:8088/api/
```

**XML Response** includes:
```xml
<input>
  <pan x="0" y="0"/>
  <zoom x="1.0" y="1.0"/>
</input>
```

### 2.4 Cropping

#### Cropping Features
- Applied per effect
- Limits effect to specific input portion
- Stacks with other effects
- Real-time processing

#### Crop Application
- Individual effect crops within effect list
- Multiple crops for layered effects

### 2.5 Effects Stack Processing

Effects are processed in order from top to bottom:
1. First effect applied
2. Second effect to result of first
3. Continue through effect chain
4. Final output to video stream

**Example Stack**:
```
1. Color Correction → Output A
2. Sharpening (on A) → Output B
3. Crop (on B) → Final Output
```

### 2.6 API Limitations for Effects

**Current Limitation**: Color correction values (Gamma, Lift, Gain, Hue, Saturation) are **not fully accessible** through the HTTP API or XML files.

- **UI Access**: Full control available in software interface
- **API Access**: Limited to reading/modifying basic properties
- **Workaround**: Use VB.NET scripting for advanced effect control
- **Status**: Community has requested expanded API access

---

## 3. INPUT LAYERS & MULTI-LAYER MIXING

### 3.1 Layer Architecture

#### MultiView Input Feature
- Combines multiple input sources into one composite input
- Supports custom layout design
- Operates independently of overlay channels
- Preserves access to all overlay channels

#### Layer Positions (MultiView)

MultiView contains 10 layers for input assignment:

| Layer | Position | Rendering Order |
|-------|----------|-----------------|
| Input 10 | Top layer | Front (rendered last) |
| Input 9 | Layer 2 | |
| Input 8 | Layer 3 | |
| ... | ... | |
| Input 2 | Layer 9 | |
| Input 1 | Back layer | Back (rendered first) |

**Rendering**: Layer 10 (topmost) renders on top; Layer 1 (bottom) renders in background.

### 3.2 Overlay Channels

vMix provides dedicated overlay channels independent of MultiView:

#### Available Overlays
- **Main Output**: Primary mix
- **Overlay 1**: First overlay channel
- **Overlay 2**: Second overlay channel
- **Overlay 3**: Third overlay channel
- **Overlay 4**: Fourth overlay channel

#### Overlay Functions (API)
Overlay state and activation controlled via API:

**API Functions**:
- Query overlay active status (via XML)
- Enable/disable overlays
- Switch overlay inputs
- Control overlay visibility and transitions

**Example XML Query**:
```xml
<overlays>
  <overlay number="1" active="true" input="5"/>
  <overlay number="2" active="false" input="0"/>
  <overlay number="3" active="true" input="7"/>
  <overlay number="4" active="false" input="0"/>
</overlays>
```

### 3.3 Layer Management API

#### Querying Layer Data

XML API provides layer information per input:

```xml
<input type="multiview">
  <layer number="1" input="2"/>
  <layer number="2" input="3"/>
  <layer number="3" input="4"/>
  ...
  <layer number="10" input="5"/>
</input>
```

#### API Limitations
- XML API returns pan X,Y and zoom X,Y per layer
- Full layer property modification limited
- User community requesting expanded layer API access

#### Programmatic Layer Control
For advanced layer manipulation:
- Use VB.NET scripting capabilities
- Implement shell script automation
- Leverage third-party REST API wrappers (e.g., GitHub REST API projects)

---

## 4. VIRTUAL CAMERA SETS & MULTIPLE CAMERA MANAGEMENT

### 4.1 Virtual Sets Overview

#### Virtual Set Capabilities
- Pre-designed customizable virtual backgrounds
- High-quality graphics integrated in software
- Multiple camera angle support
- Thumbnail preview navigation
- Professional set templates

#### Virtual Set Layers
The Setup Tab allows adjustment of various layers forming a complete Virtual Set:

| Layer Type | Purpose | Examples |
|-----------|---------|----------|
| **Camera Layers** | Primary camera feeds | Talent, Secondary talent |
| **Video Clip Layers** | Background elements | Animated backgrounds, clips |
| **Graphics Layers** | Static graphics | Lower thirds, logos |

### 4.2 Virtual Inputs (Camera Presets)

#### Purpose
Named configurations storing specific PTZ camera positions for preset switching.

#### Components
- **Pan Position**: Horizontal camera position
- **Tilt Position**: Vertical camera position  
- **Zoom Position**: Zoom level (optical/digital)

#### Preset Management
1. Create preset for each camera angle/position
2. Name preset (e.g., "Wide Shot", "Close-up", "Two-Shot")
3. Store in Virtual Input library
4. Switch between presets via API or UI

**Typical Preset Names**:
- Wide Shot
- Close-Up (Talent)
- Over-the-Shoulder (OTS)
- Two-Shot
- Product Detail

### 4.3 Multiple PTZ Camera Control

#### MultiView for Camera Management

**Setup Method**:
1. Add each PTZ camera as separate input
2. Add inputs to MultiView input (one per layer)
3. Create single MultiView composite input
4. Transition to MultiView to activate all presets simultaneously

**Effect**: Calling single MultiView input transition executes all camera presets in that layer configuration.

#### Virtual Input Transitions
When switching to a Virtual Input:
- All stored PTZ positions load simultaneously
- Smooth pan/tilt/zoom to programmed positions
- Multi-camera coordination in single transition

### 4.4 Camera Angle Switching

#### UI Method
Click thumbnail previews of camera angles to switch Virtual Set angles.

#### API Method
Use Virtual Input index selection:

```
http://127.0.0.1:8088/API/?Function=SelectIndex&Input=[VirtualSetInput]&Value=[AngleIndex]
```

**Parameters**:
- **SelectIndex**: Function to select Virtual Set camera angle
- **Input**: Virtual Set input name/GUID
- **Value**: Angle/position index number (0-based)

#### Pan/Tilt/Zoom Query via API

Current PTZ positions queryable through XML:

```xml
<input type="camera" title="Camera 1">
  <pan x="12.5" y="-5.0"/>
  <zoom x="2.0" y="2.0"/>
</input>
```

### 4.5 Virtual Webcam Output

#### External Output Feature
- Enables virtual webcam driver creation
- Outputs vMix video stream as virtual device
- Supports integration with external applications (Skype, Zoom, Teams)

**Use Cases**:
- Screen sharing in video conferences
- Multi-platform streaming
- Third-party application integration

---

## 5. INPUT PROPERTIES - QUERY & MODIFICATION

### 5.1 XML State Query

#### Basic Query Method
```
http://127.0.0.1:8088/api/
```

**Response**: Complete XML dump of vMix state including all inputs and properties.

#### XML Structure

```xml
<vmix>
  <inputs>
    <input number="1" 
           key="877bb3e7-58bd-46a1-85ce-0d673aec6bf5"
           title="Camera 1"
           type="camera"
           state="active"
           position="1"
           duration="00:00:00"
           muted="false"
           loop="false"
           selectedIndex="0">
      <pan x="0" y="0"/>
      <zoom x="1.0" y="1.0"/>
    </input>
  </inputs>
</vmix>
```

### 5.2 Input Attributes

#### Queryable Properties

| Attribute | Type | Example | Purpose |
|-----------|------|---------|---------|
| **number** | Integer | 1, 2, 3 | Input position/index |
| **key** | GUID | 877bb3e7... | Unique identifier |
| **title** | String | "Camera 1" | Display name |
| **type** | String | camera, video, image | Input type |
| **state** | String | active, paused | Current state |
| **position** | Integer | 1, 2, 3 | Mix layer position |
| **duration** | Time | 00:15:30 | Video length |
| **muted** | Boolean | true, false | Audio mute status |
| **loop** | Boolean | true, false | Video loop setting |
| **selectedIndex** | Integer | 0, 1, 2 | Selected item/variant |
| **pan x, y** | Float | 0.0, 12.5 | Pan position |
| **zoom x, y** | Float | 1.0, 2.0 | Zoom factor |

### 5.3 Text Input Properties

#### SelectedName Parameter
For Title and XAML inputs, modify specific text fields:

```
http://127.0.0.1:8088/API/?Function=SetText&Input=[InputRef]&SelectedName=[FieldName]&Value=[Text]
```

**Example**:
```
http://127.0.0.1:8088/API/?Function=SetText&Input=877bb3e7-58bd-46a1-85ce-0d673aec6bf5&SelectedName=Headline&Value=Breaking+News
```

#### GT Titles Special Syntax
For GT (Graphics Template) titles, specify field scope:

```
SelectedName=[FieldName].Text      # Text value
SelectedName=[FieldName].Source    # Image source
```

**Example**:
```
?SelectedName=Headline.Text&Value=Live+Update
?SelectedName=Logo.Source&Value=/images/logo.png
```

### 5.4 Selection Index

#### SelectedIndex Parameter
For VideoList, Virtual Set, and Title inputs with multiple options:

```
http://127.0.0.1:8088/API/?Function=SelectIndex&Input=[InputRef]&Value=[Index]
```

**Use Cases**:
- Switch Virtual Set camera angles
- Select playlist item from VideoList
- Change Title variant
- Switch video clip in sequence

**Example**:
```
?Function=SelectIndex&Input=VirtualSet&Value=2  # Select angle 2
?Function=SelectIndex&Input=Playlist&Value=0    # Select first item
```

### 5.5 Modifying Input Properties

#### Supported Modifications

| Property | Method | Example |
|----------|--------|---------|
| **Text Content** | SetText | `?Function=SetText&Input=Title1&SelectedName=Text&Value=Hello` |
| **Image** | SetImage | `?Function=SetImage&Input=Logo&Value=image.png` |
| **Position** | SetPosition | `?Function=SetPosition&Input=Input1&Value=100,50` |
| **Fader Level** | SetFader | `?Function=SetFader&Input=Audio1&Value=0.75` |
| **Add Input** | AddInput | `?Function=AddInput&Value=C:\video.mp4` |
| **Selected Index** | SelectIndex | `?Function=SelectIndex&Input=VirtualSet&Value=2` |

### 5.6 Advanced Scripting

#### VB.NET Scripting
For complex property modifications and conditional logic:

**Capabilities**:
- Access full vMix object model
- Conditional input switching
- Advanced effect parameter control
- Loop control structures
- Timer-based automation

**API Access**:
```vb
XML() ' Returns vMix state as XML
GetText(Input, Name) ' Get text field value
SetText(Input, Name, Value) ' Set text field value
```

#### Web Scripting
JavaScript-based scripting with HTTP API access:

**Capabilities**:
- API call automation
- Web-based control panels
- Cross-machine communication
- Cloud integration

### 5.7 Multi-Mix Support

#### Mix Parameter
For 4K and Pro editions with multiple mixes:

```
http://127.0.0.1:8088/API/?Function=[Function]&Mix=[MixNumber]&Input=[InputRef]
```

| Mix Value | Designation |
|-----------|------------|
| 0 | Main mix (default) |
| 1 | Secondary mix 1 |
| 2 | Secondary mix 2 |

**Example**:
```
?Function=CutDirect&Mix=0&Input=3   # Main mix
?Function=Fade&Mix=1&Duration=1000&Input=5  # Secondary mix 1
```

---

## 6. ADDITIONAL API FEATURES

### 6.1 TCP API Alternative

#### Purpose
Lower processing overhead for embedded devices with limited XML parsing.

#### Differences from HTTP API
- Uses TCP socket connection instead of HTTP
- Same command syntax
- More efficient for resource-constrained systems
- Ideal for hardware control interfaces

#### Port
Default: Network-configurable (typically 8089)

### 6.2 REST API Wrapper (Third-Party)

#### GitHub Projects
Community has created REST API wrappers:
- **curtgrimes/vmix-rest-api**: REST API and remote Web Controller access

#### Benefits
- Easier REST-style integration
- JSON request/response
- Simplified parameter handling

### 6.3 Function Discovery

#### Shortcuts Feature Method
To view all available API functions:

1. Open vMix Settings
2. Navigate to Shortcuts
3. Click "Add"
4. Browse "Function" dropdown
5. All functions available for API calls

#### Documentation References
- Official: vmix.com/help25/DeveloperAPI.html
- Unofficial: vmixapi.com (community reference)

---

## 7. IMPLEMENTATION EXAMPLES

### 7.1 Basic Input Switching Flow

```
HTTP GET http://127.0.0.1:8088/API/?Function=Fade&Duration=1000&Input=4

Response: HTTP 200 OK
Effect: Fade to Camera 4 over 1 second
```

### 7.2 Multi-Camera Preset Transition

```
1. Create Virtual Inputs with PTZ presets
   - Wide Shot: Pan 0, Tilt 0, Zoom 1.0
   - Close-up: Pan 10, Tilt -5, Zoom 2.0
   - OTS: Pan -15, Tilt 10, Zoom 1.5

2. Add cameras to MultiView layers
   - Layer 1-3: Three camera inputs

3. Switch presets via API:
   http://127.0.0.1:8088/API/?Function=SelectIndex&Input=Camera1Presets&Value=0
   
   (All cameras move to preset positions in single transition)
```

### 7.3 Dynamic Title Update

```
Step 1: Query current state
GET http://127.0.0.1:8088/api/
Response: XML with all inputs

Step 2: Find Title input GUID
<input number="5" key="abc123def456" title="Lower Third" type="title"/>

Step 3: Update text
GET http://127.0.0.1:8088/API/?Function=SetText&Input=abc123def456&SelectedName=Name&Value=John+Smith

Step 4: Make active with transition
GET http://127.0.0.1:8088/API/?Function=Fade&Duration=500&Input=5
```

---

## 8. TROUBLESHOOTING & BEST PRACTICES

### 8.1 Common Issues

#### Issue: Input Not Found
- **Cause**: Input number out of range or name mismatch
- **Solution**: Query XML to verify input number/GUID
- **Prevention**: Use GUID for reliability

#### Issue: Effects Not Applying via API
- **Cause**: Color correction parameters not accessible via API
- **Solution**: Use VB.NET scripting or UI for advanced effects
- **Workaround**: Pre-configure effects in UI, trigger via API

#### Issue: Layer Manipulation Failing
- **Cause**: API limitations on layer properties
- **Solution**: Use MultiView input switching instead
- **Alternative**: Use VB.NET scripting for layer control

### 8.2 Best Practices

1. **Use GUIDs** for reliable input references
2. **Cache XML responses** to minimize repeated queries
3. **Implement error handling** for HTTP 500 responses
4. **Test transitions** with appropriate duration values
5. **Use VB.NET scripting** for complex automation
6. **Monitor API response codes** for production stability
7. **Document custom shortcuts** for team reference
8. **Version control** API automation scripts

---

## 9. REFERENCE MATERIALS

### Official Documentation
- **HTTP Web API**: https://www.vmix.com/help25/DeveloperAPI.html
- **TCP API**: https://www.vmix.com/help25/TCPAPI.html
- **VB.NET Scripting**: https://www.vmix.com/help23/VBNetScripting.html
- **Web Scripting**: https://www.vmix.com/help23/WebScripting.html
- **Input Effects**: https://www.vmix.com/help27/InputEffects.html
- **Color Correction**: https://www.vmix.com/help24/ColourCorrection.html
- **Virtual Sets**: https://www.vmix.com/help23/VirtualSet.html

### Community Resources
- **vMix Forums**: https://forums.vmix.com/
- **Unofficial API Reference**: https://vmixapi.com/
- **GitHub Scripts**: https://github.com/rse/vmix-scripts
- **REST API Wrapper**: https://github.com/curtgrimes/vmix-rest-api
- **Community Wiki**: https://tvcrew.ch/wiki/

### Support Resources
- **StreamGeeks**: Tutorials and guides
- **Official Support**: support.vmix.com
- **Community Discord**: vMix user community

---

## 10. SESSION 3 INTEGRATION NOTES

### Recommended Integration Points

1. **Input Switching** ✅ READY
   - Implement camera switching via API
   - Use fade transitions for professional appearance

2. **Multi-Camera Management** ✅ READY
   - Use Virtual Inputs for PTZ presets
   - MultiView for composite layouts

3. **Dynamic Overlays** ⚠️ LIMITED
   - Use overlay API for activation/deactivation
   - Configure effects in UI for production

4. **Real-time Effects** ⚠️ LIMITED
   - VB.NET scripting required for advanced control
   - Pre-configure effects for API triggering

5. **Layer Manipulation** ⚠️ ADVANCED
   - Use VB.NET scripting for complex layer logic
   - Consider MultiView as primary solution

### Next Steps

1. Implement API wrapper in target language
2. Create preset configurations for camera positions
3. Develop monitoring dashboard for input states
4. Build automation scripts for recurring workflows
5. Test failover and error handling scenarios

---

**Report Generated**: November 12, 2025  
**Status**: Complete  
**Recommendation**: Ready for integration development
