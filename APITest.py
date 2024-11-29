import requests
import csv
import re


url = "https://data.ransomware.live/victims.json"

response = requests.get(url)
victim_data = response.json()[:1]

base_url = "http://10.161.44.3:7861/chat"

csv_filename = "ransomware_victims.csv"
csv_header = ["name", "country", "industry", "introduction"]
pattern_name = r"Name-(.+?)(?=;)"
pattern_country = r"Country-(.+?)(?=;)"
pattern_industry = r"Industry-(.+?)(?=;)"
pattern_introduction = r"Introduction-(.+?)(?=;)"

with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

    for victim in victim_data:
        post_title = victim['post_title']
        data = {
            "messages": [
                {"role": "user", "content": f"请以如下顺序（name, country, industry, introduction）介绍组织或个人{post_title},输出格式示例:name-名称;country-国家;industry-行业;introduction-简介;"},
            ],
            "model": "qwen2.5:latest",
            "tool_choice": "search_internet",
            "stream": True,
            "temperature": 0.7
        }
        response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)

        final_answer = ""

        for line in response.iter_content(None, decode_unicode=True):
            # 检查每一行是否包含'Final Answer'
            if 'Final Answer' in line:
                # 提取最终答案内容
                final_answer_start = line.find("Final Answer: ")
                final_answer_end = line.find('"', final_answer_start)
                if final_answer_start:
                    final_answer = line[final_answer_start:final_answer_end]
                    break  # 找到后可以退出循环
        
        print(final_answer)
        # 从final_answer中提取名称、国家、行业和简介
        if final_answer:
            name = re.findall(pattern_name, final_answer, re.DOTALL)
            country = re.findall(pattern_country, final_answer, re.DOTALL)
            industry = re.findall(pattern_industry, final_answer, re.DOTALL)
            introduction = re.findall(pattern_introduction, final_answer, re.DOTALL)
            # name = re.search(pattern_name, final_answer).group(1).strip()
            # country = re.search(pattern_country, final_answer).group(1).strip()
            # industry = re.search(pattern_industry, final_answer).group(1).strip()
            # introduction = re.search(pattern_introduction, final_answer).group(1).strip()
            print(f"Name: {name}")
            print(f"Country: {country}")
            print(f"Industry: {industry}")
            print(f"Introduction: {introduction}")

            writer.writerow([name, country, industry, introduction])
        #     # 使用正则表达式匹配名称、国家、行业和简介
        #     print(final_answer)
        #     details = re.findall(r'name：(.+?)\n\nCountry：(.+?)\n\nIndustry：(.+?)\n\nIntroduction：(.+?)(?=\n\n|\n$)', final_answer, re.DOTALL)
        #     print(details)
        #     if details:
        #         name, country, industry, introduction = details[0]
        #         writer.writerow([name, country, industry, introduction])
    
        # for line in response.iter_content(None, decode_unicode=True):
        #     print(line)


    