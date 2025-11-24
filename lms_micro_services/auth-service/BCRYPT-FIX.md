# Auth Service - bcrypt Compatibility Fix

## ⚠️ Important: bcrypt Version

This service requires **bcrypt 4.1.2** (not 5.x) due to compatibility issues with passlib 1.7.4.

## 📦 Package Versions

```
passlib==1.7.4
bcrypt==4.1.2
```

**DO NOT** use `passlib[bcrypt]` as it will install bcrypt 5.x which causes errors.

## 🐛 Issue with bcrypt 5.x

When using bcrypt 5.0.0+:
- Error: `AttributeError: module 'bcrypt' has no attribute '__about__'`
- Passlib tries to read `_bcrypt.__about__.__version__` which doesn't exist in bcrypt 4.x+

## ✅ Solution Applied

File: `app/core/security.py`

```python
import bcrypt

# Fix passlib compatibility with bcrypt 4.x
if not hasattr(bcrypt, '__about__'):
    class About:
        __version__ = '4.1.2'
    bcrypt.__about__ = About()
```

This patch makes bcrypt 4.1.2 compatible with passlib 1.7.4.

## 📝 Installation

```bash
pip install -r requirements.txt
```

This will install the correct versions automatically.

## 🔧 If You Need to Reinstall

```bash
pip uninstall bcrypt passlib -y
pip install passlib==1.7.4 bcrypt==4.1.2
```

## ✅ Verify Installation

```bash
pip show bcrypt | findstr Version
# Should show: Version: 4.1.2

pip show passlib | findstr Version
# Should show: Version: 1.7.4
```

## 🧪 Test Password Hashing

```python
from app.core.security import get_password_hash, verify_password

# Hash password
hashed = get_password_hash("admin123")
print(f"Hash: {hashed}")

# Verify password
is_valid = verify_password("admin123", hashed)
print(f"Valid: {is_valid}")  # Should be True
```

## 📚 Related Files

- `requirements.txt` - Package dependencies with pinned versions
- `app/core/security.py` - Contains the bcrypt compatibility patch
- `README-FIX-LOGIN.md` - Detailed troubleshooting guide

## 🔗 References

- [Passlib Issue](https://github.com/pyca/bcrypt/issues/684)
- [bcrypt 4.x Breaking Changes](https://github.com/pyca/bcrypt/blob/main/CHANGELOG.rst)

---

**Last Updated**: 2025-10-14
**Status**: ✅ Fixed and Working
