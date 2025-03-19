def normalize_string(s: str) -> str:
    """处理字符串：去掉首尾空格、双引号、单引号，并转换为小写"""
    if not s:
        return s
    
    # 去掉首尾空格
    s = s.strip()
    
    # 去掉首尾的双引号和单引号
    if (s.startswith('"') and s.endswith('"')) or \
       (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    
    # 转换为小写
    return s.lower()
