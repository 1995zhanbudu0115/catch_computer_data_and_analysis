# coding: utf-8
# Project:Python电脑数据分析
# Author: Alvin Du
# Contact: 63265849@qq.com

from my_function import pachong_function as pf
import json
import pandas as pd
from pyecharts import Pie, WordCloud


# 获取价格信息
def get_jd_price(url):
    sku = url.split('/')[-1].strip('.html')
    p_url = 'https://p.3.cn/prices/mgets?skuIds=J_' + sku
    res = pf.get_html_str(p_url)
    content = json.loads(res)
    good_price = float(content[0]['p'])
    return good_price


# 获取每一页的参数信息
def get_each_page(url):
    comp_info = {}
    c_soup = pf.get_html_soup(url)
    comp_list = c_soup.find_all('div', 'gl-i-wrap j-sku-item')
    for each_comp in comp_list:
        comp_name = each_comp.select('em')[-1].string.strip()
        comp_addr = each_comp.select('a')[0].get('href')
        good_addr = 'https:' + comp_addr
        each_soup = pf.get_html_soup(good_addr)
        param_list = each_soup.find_all('ul',  'parameter2 p-parameter-list')[0].select('li')
        price = get_jd_price(good_addr)
        comp_info[comp_name] = {}
        comp_info[comp_name]['价格'] = price
        try:
            for param in param_list:
                param_info = str(param.string).split('：')
                comp_info[comp_name][param_info[0]] = param_info[1]
        except:
            print('error')
            pass
    data = pd.DataFrame(comp_info).T
    return data


# 数据合成
def get_total_data(page_span):
    total_data = pd.DataFrame()
    for page_num in range(page_span):
        url = 'https://list.jd.com/list.html?cat=670,671,672&ev=6265%5F9113&page=2' % page_num + \
              '&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main'
        each_data = get_each_page(url)
        total_data = total_data.append(each_data)
        print('='*20 + 'page ' + str(page_num) + 'completed')
    total_data.to_csv('comp_data.csv')
    return total_data


# 数据可视化
def analysis(page_span):
    data = get_total_data(page_span)
    for param_column in list(data):
        param_count = data.groupby([param_column], as_index=True)[param_column].count()
        keys = list(param_count.index)
        values = list(param_count)
        attr, value = keys, values
        if list(data).index(param_column) in [8]:
            chart = WordCloud(param_column, width=800, height=500, title_pos='center')
            chart.add('', attr, value, shape="circle", is_label_show=True, is_legend_show=False,
                      is_area_show=True)
            chart.render('%s.html' % param_column)
        else:
            # 画图
            chart = Pie(param_column, width=800, height=500, title_pos='center')
            chart.add('', attr, value, center=[50, 50], redius=[10, 30], is_label_show=True, is_legend_show=False,
                      is_area_show=True)
            chart.render('%s.html' % param_column)


if __name__ == '__main__':
    span = 3
    analysis(span)


