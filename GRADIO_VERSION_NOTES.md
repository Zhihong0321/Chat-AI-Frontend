# Gradio Version Compatibility Notes

## ⚠️ CRITICAL: DO NOT CHANGE GRADIO VERSION WITHOUT READING THIS

## Working Version
- **Gradio 4.20.0** ✅ STABLE - USE THIS VERSION

## Known Broken Versions

### Gradio 4.36.1 ❌
- **Issue**: JSON schema parsing bug
- **Error**: `TypeError: argument of type 'bool' is not iterable`
- **Location**: `gradio_client/utils.py` in `_json_schema_to_python_type()`
- **Cause**: Bug in API schema generation for certain component configurations
- **Status**: AVOID THIS VERSION

### Gradio 4.44.0 ❌
- **Issue**: huggingface_hub compatibility
- **Error**: `ImportError: cannot import name 'HfFolder' from 'huggingface_hub'`
- **Cause**: Gradio 4.44.0 requires newer huggingface_hub that removed `HfFolder` class
- **Status**: AVOID THIS VERSION (requires huggingface_hub >= 0.24.0 which breaks other things)

### Gradio 4.37.x - 4.43.x ❌
- **Status**: NOT TESTED - likely have similar issues
- **Recommendation**: AVOID - stick with 4.20.0

## Why Gradio 4.20.0 Works
1. Stable API schema generation
2. Compatible with standard huggingface_hub versions
3. No known bugs with Dataframe components
4. Works with our component configuration (Dataframe, CheckboxGroup, Dropdown, etc.)
5. Proven to work in production

## If You Must Upgrade
1. Test locally first with: `pip install gradio==X.X.X`
2. Run the app: `python -m apps.ui.app`
3. Check for:
   - Import errors
   - JSON schema errors
   - Component rendering issues
   - API endpoint generation
4. Only push if ALL tests pass

## Deployment History
- Initial: Gradio 4.36.1 → JSON schema bug
- Fix attempt 1: Gradio 4.44.0 → HfFolder import error
- Final: Gradio 4.20.0 → ✅ WORKING

## Current Working requirements.txt
```
gradio==4.20.0
httpx>=0.27.0,<1.0.0
python-dotenv>=1.0.0,<2.0.0
```

## DO NOT:
- ❌ Upgrade Gradio without testing locally first
- ❌ Add huggingface_hub pinned version (let Gradio manage it)
- ❌ Add gradio-client separately (Gradio includes it)
- ❌ Use Gradio versions > 4.30.0 without thorough testing

## Last Updated
2024-11-11 - After 3 failed deployment attempts with version changes
