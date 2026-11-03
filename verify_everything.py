import os
import re
import glob

root_dir = "正文"
vol_dirs = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d.startswith("0")])

print("================================================================================")
print("COMPREHENSIVE FINAL VERIFICATION OF 《过度拟合》（OVERFITTING）")
print("================================================================================")

expected_counts = {
    "01_第一卷": 21,
    "02_第二卷": 28,
    "03_第三卷": 30,
    "04_第四卷": 30,
    "05_第五卷": 28,
    "06_第六卷": 25,
    "07_第七卷": 28,
    "08_第八卷": 21
}

total_chapters = 0
total_chars = 0
violations = []

for v, exp_cnt in expected_counts.items():
    v_path = os.path.join(root_dir, v)
    c_files = sorted([f for f in os.listdir(v_path) if f.endswith(".md") and f.startswith("第")])
    actual_cnt = len(c_files)
    print(f"Checking {v}: Expected {exp_cnt} chapters, found {actual_cnt} chapters.")
    if actual_cnt != exp_cnt:
        violations.append(f"{v}: chapter count mismatch (expected {exp_cnt}, found {actual_cnt})")
    
    vol_chars = 0
    for f in c_files:
        f_path = os.path.join(v_path, f)
        with open(f_path, "r", encoding="utf-8") as fp:
            text = fp.read()
        cnt = len(re.findall(r'[\u4e00-\u9fa5]', text))
        vol_chars += cnt
        total_chars += cnt
        total_chapters += 1
        
        # Word count check
        if cnt < 2600 or cnt > 3000:
            violations.append(f"{v}/{f}: word count {cnt} out of bounds (2600-3000)")
        
        # POV check: First person '我' should be present
        if "我" not in text:
            violations.append(f"{v}/{f}: missing first person POV '我'")

    print(f"  -> Total characters in {v}: {vol_chars} Chinese chars. Average per chapter: {vol_chars/actual_cnt:.1f}")

print("--------------------------------------------------------------------------------")
print(f"Total Chapters Verified: {total_chapters} (Expected: 211)")
print(f"Total Pure Chinese Characters: {total_chars} chars (~{total_chars/10000:.2f} 万字)")
print(f"Total Violations: {len(violations)}")
if violations:
    print("VIOLATIONS LIST:")
    for viol in violations:
        print("  -", viol)
else:
    print("ALL 211 CHAPTERS ARE 100% PERFECTLY COMPLIANT!")
print("================================================================================")
