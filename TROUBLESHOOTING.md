# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### ❌ "streamlit: command not found"

**Problem:** Streamlit was installed in user directory not in PATH

**Solution:** Use `python3 -m streamlit` instead of just `streamlit`

```bash
# ❌ Don't use:
streamlit run app.py

# ✅ Use:
python3 -m streamlit run app.py
```

**The `run_dashboard.sh` script has been updated to use this method.**

---

### ❌ "No module named 'streamlit'" (or other modules)

**Problem:** Dependencies not installed

**Solution:**
```bash
pip3 install --user -r requirements.txt
```

**Verify installation:**
```bash
python3 -c "import streamlit, pandas, plotly, yaml; print('✅ All installed')"
```

---

### ❌ "FileNotFoundError: data/generated/..."

**Problem:** Mock data hasn't been generated yet

**Solution:**
```bash
cd data/generators
python3 generate_all_data.py
cd ../..
```

**Verify data exists:**
```bash
ls -lh data/generated/
# Should show 13 .parquet files
```

---

### ❌ Port 8501 already in use

**Problem:** Another Streamlit app or process is using the port

**Solution 1 - Use different port:**
```bash
python3 -m streamlit run app.py --server.port 8502
```

**Solution 2 - Kill existing process:**
```bash
# Find the process
lsof -i :8501

# Kill it (replace PID with actual process ID)
kill -9 <PID>
```

---

### ⚠️ "No runtime found, using MemoryCacheStorageManager"

**Problem:** This is NOT an error!

**Explanation:** This warning appears when importing Streamlit modules outside the runtime (e.g., during testing). It's harmless and won't appear when running the actual dashboard.

**Action:** Ignore this warning - dashboard will work fine.

---

### ❌ Charts not displaying / blank page

**Problem:** Browser cache or Streamlit cache issues

**Solution:**
```bash
# Clear Streamlit cache
python3 -m streamlit cache clear

# Restart dashboard
python3 -m streamlit run app.py
```

**Alternative:** Try a different browser or incognito/private mode

---

### ⚠️ "OpenAI API key not configured"

**Problem:** This is NOT an error if you haven't set up API key

**Explanation:** The chatbot will use rule-based fallback analysis (still very effective!)

**To enable full AI (optional):**
1. Get API key from https://platform.openai.com/
2. Create `.env` file: `cp .env.template .env`
3. Add key: `OPENAI_API_KEY=sk-your-key-here`
4. Restart dashboard

---

### ❌ "ModuleNotFoundError: No module named 'src'"

**Problem:** Running from wrong directory

**Solution:** Always run from project root:
```bash
cd "/Users/adityasharma/Airport CxO Dash"
python3 -m streamlit run app.py
```

---

### ❌ Permission denied: ./run_dashboard.sh

**Problem:** Script not executable

**Solution:**
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

---

### 🐌 Dashboard very slow on first load

**Problem:** Streamlit is loading and caching all data

**Explanation:** This is normal! The first load can take 10-20 seconds.

**What's happening:**
- Loading 13 parquet files (~200KB total)
- Creating data indices
- Caching for fast subsequent loads

**Subsequent loads will be instant** thanks to `@st.cache_data`

---

### ❌ Import errors in custom code

**Problem:** Python can't find custom modules

**Solution:** Ensure you have `__init__.py` files in all directories:
```bash
# Verify __init__.py files exist
ls src/__init__.py
ls src/dashboard/__init__.py
ls src/dashboard/components/__init__.py
ls src/dashboard/pages/__init__.py
ls src/ai/__init__.py
ls src/utils/__init__.py
```

All should exist (they're already created).

---

### 🔍 Debug Mode

To see detailed error messages:

```bash
python3 -m streamlit run app.py --logger.level=debug
```

---

### ✅ Verify Everything Works

Run this comprehensive check:

```bash
cd "/Users/adityasharma/Airport CxO Dash"

echo "1. Checking Python version..."
python3 --version

echo -e "\n2. Checking dependencies..."
python3 -c "import streamlit, pandas, plotly, yaml, numpy; print('✅ All installed')"

echo -e "\n3. Checking data files..."
ls data/generated/*.parquet | wc -l
echo "Should show: 13"

echo -e "\n4. Checking app syntax..."
python3 -m py_compile app.py && echo "✅ Syntax valid"

echo -e "\n5. Testing imports..."
python3 -c "from src.utils.data_loader import DataLoader; print('✅ Imports work')"

echo -e "\n✅ All checks passed! Run: ./run_dashboard.sh"
```

---

### 📧 Still Having Issues?

1. Check [README.md](README.md) for full documentation
2. Review [QUICKSTART.md](QUICKSTART.md) for setup steps
3. Ensure all files were created correctly
4. Try running individual Python files to isolate the issue

---

### 🔄 Fresh Start (Nuclear Option)

If all else fails, clean restart:

```bash
# 1. Clean Python cache
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 2. Clear Streamlit cache
python3 -m streamlit cache clear

# 3. Regenerate data
cd data/generators
rm -rf ../generated/*.parquet
python3 generate_all_data.py
cd ../..

# 4. Reinstall dependencies
pip3 install --user --upgrade -r requirements.txt

# 5. Run dashboard
python3 -m streamlit run app.py
```

---

## Quick Reference

### ✅ Working Commands
```bash
# Run dashboard
./run_dashboard.sh
# OR
python3 -m streamlit run app.py

# Generate data
cd data/generators && python3 generate_all_data.py

# Install dependencies
pip3 install --user -r requirements.txt

# Clear cache
python3 -m streamlit cache clear
```

### ❌ Don't Use These
```bash
streamlit run app.py        # streamlit not in PATH
python app.py               # This is a Streamlit app, not a script
cd src && python3 app.py    # Wrong directory
```

---

**Everything verified working? Great! Run:**
```bash
./run_dashboard.sh
```

And navigate to http://localhost:8501 🚀
