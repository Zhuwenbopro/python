import time
import datetime
import requests
from lxml import etree
import csv

filename = './trending_targets.csv'
destination = './data/'
headers = {
    'authority': 'tophub.today',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://tophub.today/',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0',
}
sleep_time = 60 # 秒
today = datetime.date.today()
def init():
    data = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        # header = next(csv_reader)        # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到data中
            data.append(row)  # 选择某一列加入到data数组中
    apps = data[0]
    links = data[1]
    lists = []
    for _ in apps:
        lists.append({})
    return apps, links, lists
apps, links, lists = init()

def getList(r):
    tree = etree.HTML(r.content.decode('utf-8'))
    tables = tree.xpath('//table[@class="table"]')
    t = tables[0]
    items = t.xpath('//td[@class="al"]/a/text()')
    hrefs = t.xpath('//td[@class="al"]/a/@href')
    return items, hrefs
def writefile(filename, content):
    with open(filename, "a", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        if isinstance(content, list):
            for i in content:
                csv_writer.writerow(i)
        else: csv_writer.writerow(content)
        f.close()
def check_and_save(list, items, hrefs, app):
    into_file = destination + today.strftime('%Y-%m-%d') + '.csv'
    # print(into_file)
    lines = []
    for n, item in enumerate(items):
        if item in list:
            continue
        else:
            lines.append([item, app, hrefs[n], datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')])
            list[item] = hrefs[n]
    # print(lines)
    if len(lines) != 0:
        writefile(into_file, lines)
    else: print('没什么好记的！')


while True:
    if today != datetime.date.today():
        today = datetime.date.today()
        apps, links, lists = init()
    for i, link in enumerate(links):
        try:
            response = requests.get(link, headers=headers)
            items, hrefs = getList(response)
            # print(items)
            check_and_save(lists[i], items, hrefs, apps[i])
            time.sleep(sleep_time)
        except Exception as err:
            writefile('./log.txt', err)