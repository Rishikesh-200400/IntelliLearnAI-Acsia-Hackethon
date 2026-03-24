# Background Image Setup

## Current Setup

The app currently uses an **animated teal gradient background** that matches the color scheme of your skills image (#84BDC3).

## To Use Your Custom Image

If you want to use your actual "SKILLS" image as the background:

1. **Save your image** as `skills-background.png` or `skills-background.jpg` in this folder
   
2. **Update the CSS** in `app.py`, replace this line:
   ```css
   background: linear-gradient(135deg, #88c5cc 0%, #7eb5bd 25%, #84BDC3 50%, #90ccd3 75%, #88c5cc 100%);
   ```
   
   With:
   ```css
   background-image: url('./static/images/skills-background.png');
   background-size: cover;
   background-position: center;
   background-repeat: no-repeat;
   background-attachment: fixed;
   ```

3. **Adjust transparency** in the `.block-container` CSS for better readability over the image

## Current Benefits

The animated gradient provides:
- ✅ **Smooth performance** (no image loading)
- ✅ **Professional look** with subtle animations
- ✅ **Perfect readability** with glass-morphism effect
- ✅ **Matches your color scheme** (#84BDC3 teal)
- ✅ **Responsive** across all screen sizes

## Image Saved Here

Place your background image in:
`c:\Users\rajis\OneDrive\Documents\hackathon\static\images\`
