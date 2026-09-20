# Queue Management System - Unified CSS

## Overview
This project now uses a unified, professional CSS design system across all HTML templates. All inline styles have been removed and replaced with a comprehensive CSS framework.

## CSS File Location
- **Main CSS**: `app1/static/css/main.css`
- **Compiled CSS**: `staticfiles/css/main.css` (after running `collectstatic`)

## Design Features

### 🎨 **Modern Design System**
- Consistent color scheme with primary colors: `#667eea` and `#764ba2`
- Professional typography using Segoe UI font family
- Smooth gradients and modern shadows
- Responsive design for all screen sizes

### 🧩 **Component Library**
- **Cards**: `.card`, `.card-large`, `.card-full`
- **Buttons**: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`
- **Forms**: `.form-group`, `.form-label`, `.form-input`
- **Tables**: `.table-container`, `.table`
- **Stats**: `.stats-grid`, `.stat-card`
- **Navigation**: `.nav-grid`, `.nav-card`
- **Alerts**: `.alert`, `.alert-success`, `.alert-error`, `.alert-warning`, `.alert-info`

### 📱 **Responsive Design**
- Mobile-first approach
- Breakpoints: 768px (tablet), 480px (mobile)
- Flexible grid systems
- Touch-friendly button sizes

### 🎭 **Interactive Elements**
- Hover effects on cards and buttons
- Smooth transitions and animations
- Focus states for form inputs
- Custom scrollbar styling

## Usage Examples

### Basic Page Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
    <link rel="stylesheet" href="cssmain.css">
</head>
<body>
    <div class="page-container">
        <div class="card">
            <div class="header">
                <div class="logo">🎯</div>
                <h1 class="title">Page Title</h1>
                <p class="subtitle">Page description</p>
            </div>
            <!-- Content here -->
        </div>
    </div>
</body>
</html>
```

### Dashboard Layout
```html
<div class="container">
    <div class="header">
        <div class="logo">📊</div>
        <h1 class="title">Dashboard</h1>
        <p class="subtitle">Overview and statistics</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-number">42</div>
            <div class="stat-label">Total Users</div>
        </div>
    </div>
    
    <div class="nav-grid">
        <a href="#" class="nav-card">
            <div class="nav-icon">🔢</div>
            <div class="nav-title">Action</div>
            <div class="nav-description">Description</div>
        </a>
    </div>
</div>
```

### Form Elements
```html
<div class="form-group">
    <label class="form-label" for="email">Email Address</label>
    <input type="email" id="email" name="email" class="form-input" required>
</div>

<div class="btn-container">
    <button type="submit" class="btn btn-primary btn-full">Submit</button>
    <a href="#" class="btn btn-secondary btn-full">Cancel</a>
</div>
```

## Utility Classes

### Spacing
- `.mb-0` to `.mb-4` - Margin bottom
- `.mt-0` to `.mt-4` - Margin top
- `.p-0` to `.p-4` - Padding

### Text Alignment
- `.text-center` - Center align text
- `.text-left` - Left align text
- `.text-right` - Right align text

### Button Modifiers
- `.btn-full` - Full width button
- `.btn-large` - Larger button size

## Color Palette

### Primary Colors
- **Primary**: `#667eea` (Blue)
- **Secondary**: `#764ba2` (Purple)
- **Success**: `#27ae60` (Green)
- **Danger**: `#e74c3c` (Red)
- **Warning**: `#f39c12` (Orange)

### Text Colors
- **Primary Text**: `#2c3e50` (Dark)
- **Secondary Text**: `#7f8c8d` (Gray)
- **Light Text**: `#bdc3c7` (Light Gray)

### Background Colors
- **Primary BG**: `#f8f9fa` (Light Gray)
- **Card BG**: `#ffffff` (White)
- **Hover BG**: `#e9ecef` (Hover Gray)

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile devices
- Progressive enhancement approach

## Maintenance
- All styles are centralized in `main.css`
- Easy to modify colors, spacing, and components
- Consistent design language across all pages
- No more inline styles to maintain

## Migration Notes
- All HTML templates have been updated to use the new CSS classes
- Inline styles have been removed
- Bootstrap dependencies have been eliminated
- Custom CSS classes provide all necessary functionality
