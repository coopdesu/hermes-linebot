#!/usr/bin/env python3
"""Enrich leathers.json with visual characteristics and identification data."""
import json

# Enrichment data based on expert knowledge of Hermès leathers
ENRICHMENT = {
    "Togo": {
        "description_zh": "柔軟度適中、紋路大小適中的公小牛皮。1997年問世後因易於保養而大受歡迎，是Birkin、Kelly最常見的皮革。輕微抓痕可自行修復。",
        "visual_characteristics": "中等大小的圓形顆粒紋路，紋路自然不規則，表面帶有輕微啞光感，整體看起來飽滿圓潤",
        "texture": "柔軟有彈性，手感溫潤，輕壓後可回彈",
        "how_to_identify": "顆粒比Clemence小、比Epsom大；紋路圓且自然；側面看包型較挺；比Clemence更能保持形狀",
        "common_items": "Birkin, Kelly, Lindy, Evelyne, 小皮件",
        "market_value": "市場流通性最高，Togo+金色+GHW為最經典組合，保值性強，建議積極收購",
        "scratch_resistance": "中等，輕微刮痕可自行癒合",
        "shine_level": "啞光至半光"
    },
    "Clemence": {
        "description_zh": "曾稱為Mou的公成牛皮，質地柔軟下垂，觸感豐厚。顆粒比Togo大，包型較不挺，但色彩飽和度高。",
        "visual_characteristics": "顆粒比Togo明顯更大，紋路分布較稀疏，表面帶有自然蠟感光澤，整體看起來較為豐厚",
        "texture": "非常柔軟，有點垂墜感，類似奶油質地",
        "how_to_identify": "顆粒是常見牛皮中最大的；包型較軟不挺；比Togo更有垂墜感；顏色飽和度高",
        "common_items": "Birkin, Kelly, Lindy, Picotin",
        "market_value": "流通性高，顏色選擇多，適合日常使用，收購價值穩定",
        "scratch_resistance": "中等，輕微刮痕較難完全自癒",
        "shine_level": "自然蠟感，半光澤"
    },
    "Epsom": {
        "description_zh": "經壓花處理的公小牛皮，表面有細密均勻的十字紋壓印。2003年問世，因結構挺括、耐用、防水性佳而廣受歡迎。",
        "visual_characteristics": "細密均勻的格子狀/十字狀壓紋，非常整齊規律，表面較硬挺，啞光感強",
        "texture": "偏硬挺，有結構感，不像Togo般柔軟",
        "how_to_identify": "唯一帶有明顯規律壓紋的主流皮革；紋路非常整齊均勻；包型最挺；重量較輕",
        "common_items": "Birkin, Kelly, Constance, Bolide, 錢包, 小皮件",
        "market_value": "最受市場歡迎之一，特別是Kelly；維護容易，收購建議積極",
        "scratch_resistance": "最強，壓紋可掩蓋細小刮痕",
        "shine_level": "啞光"
    },
    "Swift": {
        "description_zh": "光滑細膩的小牛皮，無明顯紋路，表面光澤感強。質地細緻柔軟，是皮革中最精緻的之一，但較容易留下刮痕。",
        "visual_characteristics": "表面光滑幾乎無紋路，光澤感明顯，可看出皮革本身的細膩毛孔",
        "texture": "非常柔軟細膩，類似絲緞感",
        "how_to_identify": "表面最光滑的牛皮；有明顯光澤；與Box Calf類似但Swift更薄更柔軟；毛孔細小",
        "common_items": "Kelly, Birkin, Constance, Mini Kelly, 錢包",
        "market_value": "因容易刮傷，使用痕跡較明顯，收購時需仔細檢查成色，AB以上才建議積極收購",
        "scratch_resistance": "較弱，容易留下刮痕和指甲印",
        "shine_level": "高光澤"
    },
    "Box Calf": {
        "description_zh": "愛馬仕最經典的皮革之一，歷史悠久。光滑有光澤的小牛皮，使用後會產生自然的Patina（皮革包漿），是愛馬仕收藏家最珍視的皮革。",
        "visual_characteristics": "表面光滑，光澤感強烈，使用後會發展出深邃的包漿光澤（Patina）",
        "texture": "硬挺有結構，使用後逐漸變柔軟",
        "how_to_identify": "高光澤；使用後顏色會加深並產生美麗包漿；刮痕可通過拋光修復；比Swift更厚實",
        "common_items": "Kelly, Birkin, 錢包, 手環",
        "market_value": "老vintage款收藏價值極高，有好Patina的Box Calf是藏家首選，建議積極收購",
        "scratch_resistance": "中等，刮痕可用手指或布料摩擦修復",
        "shine_level": "高光澤，越用越亮"
    },
    "Barenia": {
        "description_zh": "無染色的天然植鞣小牛皮，愛馬仕最古老的皮革之一。使用後顏色會自然加深（Patina），極受收藏家珍視。",
        "visual_characteristics": "表面光滑，自然蜜蠟色（米黃至淺棕），使用後逐漸加深為蜂蜜棕色",
        "texture": "柔軟有油脂感，質地豐厚",
        "how_to_identify": "通常只有自然原色（Natural/Fauve）；使用後顏色明顯加深；有獨特的蠟感光澤；非常罕見",
        "common_items": "Sac à dépêches, Kelly, 馬具配件",
        "market_value": "極稀有，市場流通性低，收到即建議收購，是收藏家頂級品",
        "scratch_resistance": "中等，輕微刮痕可用手指熱度修復",
        "shine_level": "自然蠟感光澤"
    },
    "Barenia Faubourg": {
        "description_zh": "Barenia的現代版本，保留了原版的自然質感和包漿特性，但更適合現代製包工藝。",
        "visual_characteristics": "與Barenia相似，光滑表面帶有明顯凹凸紋路，自然光澤",
        "texture": "柔軟有彈性，有油潤感",
        "how_to_identify": "比原版Barenia稍硬挺；有輕微紋路；通常為自然色系",
        "common_items": "Birkin, Kelly, 皮帶",
        "market_value": "稀有度高，建議收購",
        "scratch_resistance": "中等",
        "shine_level": "自然光澤"
    },
    "Chevre Mysore": {
        "description_zh": "產自印度的山羊皮，表面有細密的天然顆粒紋路，光澤感強，色彩飽和度高，是愛馬仕小皮件最常用的皮革之一。",
        "visual_characteristics": "非常細小密集的天然顆粒紋路，光澤感比牛皮更強，顏色看起來更鮮艷飽和",
        "texture": "輕薄但有韌性，比牛皮更有彈性",
        "how_to_identify": "紋路比任何牛皮都細小；光澤感強；顏色特別鮮艷；重量較輕；主要用於錢包、小皮件",
        "common_items": "Bearn錢包, Dogon錢包, Azap錢包, Kelly小包",
        "market_value": "小皮件常見皮革，耐用性高，流通性強，建議收購",
        "scratch_resistance": "強，山羊皮天然耐刮",
        "shine_level": "高光澤"
    },
    "Porosus Crocodile": {
        "description_zh": "最頂級的鱷魚皮，來自泰國暹羅鱷（Saltwater Crocodile）。鱗片細小均勻，紋路規律美觀，是愛馬仕鱷魚皮中最珍貴的品種。",
        "visual_characteristics": "鱗片細小且非常均勻，腹部中心線清晰，鱗片有天然的凹凸立體感，光澤感極強",
        "texture": "硬挺，有涼感，鱗片邊緣可感受到輕微起伏",
        "how_to_identify": "鱗片最小最均勻（vs Niloticus更大）；腹部鱗片排列最規律；是最貴的鱷魚皮",
        "common_items": "Birkin, Kelly (頂級訂製款)",
        "market_value": "最高收藏價值，收到即建議積極收購，保值性最強",
        "scratch_resistance": "強",
        "shine_level": "高光澤（亮面）或啞光（Matte版）"
    },
    "Niloticus Crocodile": {
        "description_zh": "尼羅河鱷魚皮，鱗片比Porosus稍大，同樣來自非洲尼羅鱷。是愛馬仕鱷魚皮中的第二珍貴品種。",
        "visual_characteristics": "鱗片比Porosus大，腹部中心線較寬，鱗片邊緣更明顯",
        "texture": "硬挺，鱗片感更明顯",
        "how_to_identify": "鱗片比Porosus大且更不規則；腹部寬度較大；整體看起來更「有份量」",
        "common_items": "Birkin, Kelly",
        "market_value": "極高收藏價值，積極建議收購",
        "scratch_resistance": "強",
        "shine_level": "高光澤（亮面）或啞光（Matte版）"
    },
    "Ostrich": {
        "description_zh": "鴕鳥皮，以其獨特的毛孔凸起（Quill bumps）聞名，每個凸起都是曾長有羽毛的毛孔。輕盈且非常耐用。",
        "visual_characteristics": "有明顯的圓形凸起（毛孔），排列不規則但密集，腹部中心部位凸起最明顯，四周漸漸平滑",
        "texture": "輕盈柔軟，凸起部位觸感圓潤",
        "how_to_identify": "最獨特：有明顯的3D凸起毛孔；腹部中心凸起最大最密集；重量比牛皮輕得多",
        "common_items": "Birkin, Kelly, 小皮件",
        "market_value": "流通性高，顏色選擇多，建議收購，特別是稀有色",
        "scratch_resistance": "強",
        "shine_level": "半光澤至高光澤"
    },
    "Fjord": {
        "description_zh": "啞光感強的小母牛皮，耐水性在牛皮中最佳，較少用於Birkin/Kelly，多見於休閒款包型。",
        "visual_characteristics": "表面有細小紋路，整體看起來啞光，比Togo更平整",
        "texture": "偏硬挺，有韌性",
        "how_to_identify": "比Togo啞光；耐水性好；多用於Garden Party等休閒款",
        "common_items": "Garden Party, Evelyne",
        "market_value": "流通性中等",
        "scratch_resistance": "強",
        "shine_level": "啞光"
    },
    "Lizard": {
        "description_zh": "蜥蜴皮，以細小均勻的鱗片著稱。主要用於小皮件，偶爾用於小型包款。色彩豐富，光澤感強。",
        "visual_characteristics": "非常細小整齊的鱗片，排列規律如馬賽克，光澤感強",
        "texture": "光滑，鱗片邊緣幾乎感受不到",
        "how_to_identify": "鱗片最小最密集的異材；排列最規律整齊；常見於小皮件",
        "common_items": "Constance (mini), 錢包, Kelly手環",
        "market_value": "稀有，建議收購",
        "scratch_resistance": "中等",
        "shine_level": "高光澤"
    },
    "Toile H": {
        "description_zh": "愛馬仕標誌性的帆布材質，常與皮革搭配使用。耐用、輕盈，有多種圖案（素色、H字紋等）。",
        "visual_characteristics": "織物質感，可見明顯的編織紋路，通常與皮革提把和飾邊搭配",
        "texture": "硬挺的帆布感",
        "how_to_identify": "織物非皮革；常與皮革混搭；有H字樣或素色設計",
        "common_items": "Herbag, Garden Party, 部分Birkin特殊款",
        "market_value": "流通性中等，特殊組合收購價值高",
        "scratch_resistance": "強（帆布）",
        "shine_level": "無光澤"
    },
    "Madame": {
        "description_zh": "與Epsom類似的壓紋小牛皮，但紋路更細緻，光澤感略強於Epsom，質地比Epsom稍柔軟。",
        "visual_characteristics": "細密壓紋，比Epsom紋路略細，表面有輕微光澤",
        "texture": "比Epsom稍柔軟",
        "how_to_identify": "與Epsom非常相似；紋路稍細；光澤比Epsom略強",
        "common_items": "Constance, Kelly, 錢包",
        "market_value": "流通性高，建議收購",
        "scratch_resistance": "強",
        "shine_level": "半光澤"
    },
    "Evercolor": {
        "description_zh": "2013年問世的公小牛皮，啞光感強，硬度適中，色彩非常鮮豔飽和，是近年熱門選擇。",
        "visual_characteristics": "表面紋路細小，整體啞光，顏色特別鮮艷",
        "texture": "硬度中等，有輕微顆粒感",
        "how_to_identify": "顏色比其他牛皮更鮮艷飽和；啞光感強；近年常見於Constance和Kelly",
        "common_items": "Constance, Kelly, 錢包",
        "market_value": "近年熱門，特別是鮮豔色，建議積極收購",
        "scratch_resistance": "強",
        "shine_level": "啞光"
    },
    "Veau Velours": {
        "description_zh": "麂皮（絨面革），表面有細膩絨毛質感。非常柔軟，但容易吸附灰塵和污漬，保養需謹慎。",
        "visual_characteristics": "細膩絨毛表面，不反光，有天鵝絨般質感",
        "texture": "極度柔軟，絨毛觸感",
        "how_to_identify": "唯一有絨毛表面的非異材皮革；不反光；觸感最柔軟",
        "common_items": "Constance, Kelly (特殊款)",
        "market_value": "收購需謹慎，容易有使用痕跡，AB以上才建議收購",
        "scratch_resistance": "弱，容易沾污",
        "shine_level": "無光澤（絨面）"
    }
}

# Load existing data
with open('/Users/chouchengyen/Downloads/coopy/leathers.json', encoding='utf-8') as f:
    leathers = json.load(f)

# Apply enrichment
enriched_count = 0
for leather in leathers:
    name_en = leather['name_en']
    if name_en in ENRICHMENT:
        data = ENRICHMENT[name_en]
        leather['description_zh'] = data.get('description_zh', '')
        leather['visual_characteristics'] = data.get('visual_characteristics', '')
        leather['texture'] = data.get('texture', '')
        leather['how_to_identify'] = data.get('how_to_identify', '')
        leather['common_items'] = data.get('common_items', '')
        leather['market_value'] = data.get('market_value', '')
        leather['scratch_resistance'] = data.get('scratch_resistance', '')
        leather['shine_level'] = data.get('shine_level', '')
        enriched_count += 1
    else:
        # Add empty fields for consistency
        for field in ['description_zh', 'visual_characteristics', 'texture',
                      'how_to_identify', 'common_items', 'market_value',
                      'scratch_resistance', 'shine_level']:
            if field not in leather:
                leather[field] = ''

# Save
with open('/Users/chouchengyen/Downloads/coopy/leathers.json', 'w', encoding='utf-8') as f:
    json.dump(leathers, f, ensure_ascii=False, indent=2)

print(f"完成！共 {len(leathers)} 筆，其中 {enriched_count} 筆有完整辨識資料")
print(f"未enriched: {[l['name_en'] for l in leathers if not l.get('description_zh')]}")
