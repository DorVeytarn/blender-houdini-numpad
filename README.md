# Houdini Numpad Style Editor for Blender

A Blender addon that brings Houdini's intuitive numpad-style value editor to any number field in Blender.

## Features

- **Middle-click on any number field** to activate the numpad editor
- **Vertical mouse movement** - Select the step size (1000, 100, 10, 1, 0.1, 0.01, 0.001)
- **Horizontal mouse movement** - Change the value with the selected step size
- **Real-time updates** - Values update instantly as you drag
- **Works on ANY number field** - Transform properties, modifiers, custom properties, etc.

## Installation

1. Download this addon folder
2. Open Blender Preferences → Add-ons
3. Click "Install..."
4. Navigate to the addon folder and select it
5. Enable the addon in the list

## Usage

1. Select an object in your scene
2. Open the Properties panel
3. Navigate to any property with a number field
4. **Press and hold Middle Mouse Button (MMB)** on the number field
5. **Move your mouse UP/DOWN** to select the step size (it will highlight)
6. **Move your mouse LEFT/RIGHT** to change the value
   - Moving right increases the value
   - Moving left decreases the value
7. **Release MMB** to confirm the change
8. **Press ESC or RMB** to cancel and restore the original value

## Keyboard Shortcut

- **Middle Mouse Button (MMB)** - Activate numpad editor on number fields

## Example Workflow

Adjusting object location with precision:

1. Click MMB on the Location X field
2. Move mouse down to select step "0.1" 
3. Move mouse right to increase X by 0.1 increments
4. Release MMB when satisfied
5. Repeat for Y and Z if needed

## Compatibility

- Blender 5.1+
- Works with Windows, macOS, and Linux

## Author

DorVeytarn
