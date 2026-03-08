# Confidence Score Display Fix

## Problem
The confidence score from the backend response wasn't matching the display in the frontend HTML.

## Root Cause
The frontend JavaScript was not properly validating and constraining the confidence value:
1. The confidence value could be outside the 0-100 range
2. The value wasn't being properly converted to a number
3. No rounding was applied for display

## Solution
Updated `static/script.js` in the `displayResult()` function:

### Changes Made:

1. **Added Confidence Validation**
   ```javascript
   const confidence = Math.min(Math.max(parseFloat(result.confidence) || 0, 0), 100);
   ```
   - Converts confidence to a number using `parseFloat()`
   - Defaults to 0 if not a valid number
   - Constrains value between 0 and 100 using `Math.min()` and `Math.max()`

2. **Updated Confidence Bar Display**
   ```javascript
   <div class="confidence-fill" style="width: ${confidence}%">
       ${Math.round(confidence)}%
   </div>
   ```
   - Uses the validated `confidence` variable
   - Rounds the value for cleaner display
   - Ensures width percentage is always valid

## Backend Response Format
The backend sends confidence as a number (e.g., `95`), which is correct:
```json
{
  "status": "VERIFIED",
  "confidence": 95,
  "explanation": "..."
}
```

## Frontend Display
Now correctly displays:
- ✅ Confidence bar width matches the percentage value
- ✅ Confidence text shows rounded percentage (e.g., "95%")
- ✅ Values are constrained between 0-100%
- ✅ Handles edge cases (null, undefined, out-of-range values)

## Testing
To verify the fix works:
1. Submit a claim for verification
2. Check that the confidence bar width matches the percentage text
3. Verify the value is between 0-100%

Example:
- Backend sends: `"confidence": 95`
- Frontend displays: Bar width 95%, text "95%"
