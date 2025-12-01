# -*- coding: utf-8 -*-
from . import ad_2_addr_dict
from . import _fill_adcode
from collections import defaultdict
import itertools
import operator


def ad2addr(part_adcode):
    return ad_2_addr_dict[_fill_adcode(part_adcode)]


def draw_locations(adcodes, file_path):
    """
    基于folium生成地域分布的热力图的html文件.
    :param adcodes: 地址集
    :param file_path: 生成的html文件的路径.
    """
    import folium
    from folium.plugins import HeatMap

    adcodes = filter(None, adcodes)

    # 注意判断key是否存在
    heatData = []
    for adcode in adcodes:
        attr_info = ad2addr(adcode)
        if not attr_info.latitude or not attr_info.longitude:
            continue
        heatData.append([float(attr_info.latitude), float(attr_info.longitude), 1])
    # 绘制Map，开始缩放程度是5倍
    map_osm = folium.Map(location=[35, 110], zoom_start=5)
    # 将热力图添加到前面建立的map里
    HeatMap(heatData).add_to(map_osm)
    # 保存为html文件
    map_osm.save(file_path)


def echarts_draw(
    adcodes, file_path, title="地域分布图", subtitle="location distribute"
):
    """
    生成地域分布的echarts热力图的html文件.
    :param adcodes: 地址集
    :param file_path: 生成的html文件路径.
    :param title: 图表的标题
    :param subtitle: 图表的子标题
    """
    from pyecharts.charts import Geo
    from pyecharts import options as opts

    # 过滤 None
    # 过滤掉缺乏经纬度数据的地点
    coordinates = {}
    counter = defaultdict(int)
    for adcode in filter(None, adcodes):
        addr = ad2addr(adcode)
        if not addr.longitude or not addr.latitude:
            continue
        counter[adcode] = counter[adcode] + 1
        coordinates[adcode] = (float(addr.longitude), float(addr.latitude))

    # 准备数据
    data = [(adcode, count) for adcode, count in counter.items()]

    geo = Geo(
        init_opts=opts.InitOpts(width="1200px", height="600px", bg_color="#404a59")
    )

    # 添加坐标
    for adcode, coord in coordinates.items():
        geo.add_coordinate(adcode, coord[0], coord[1])

    geo = geo.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            subtitle=subtitle,
            title_textstyle_opts=opts.TextStyleOpts(color="#fff"),
            pos_left="center",
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            textstyle_opts=opts.TextStyleOpts(color="#fff"),
            is_piecewise=True,
            pieces=[
                {"min": 1, "max": 10, "label": "1-10"},
                {"min": 11, "max": 50, "label": "11-50"},
                {"min": 51, "max": 100, "label": "51-100"},
                {"min": 101, "max": 500, "label": "101-500"},
                {"min": 501, "label": "501+"},
            ],
        ),
    ).add(
        "",
        data,
        type_="heatmap",
    )
    geo.render(file_path)


def echarts_cate_draw(
    adcodes,
    labels,
    file_path,
    title="地域分布图",
    subtitle="location distribute",
    point_size=7,
):
    """
    依据分类生成地域分布的echarts散点图的html文件.
    :param adcodes: 地址集
    :param labels: 长度必须和locations相等, 代表每个样本所属的分类.
    :param file_path: 生成的html文件路径.
    :param title: 图表的标题
    :param subtitle: 图表的子标题
    :param point_size: 每个散点的大小
    """

    if len(adcodes) != len(labels):
        from .exceptions import CPCAException

        raise CPCAException("locations的长度与labels长度必须相等")

    # 过滤 None
    # 过滤掉缺乏经纬度数据的地点
    coordinates = {}
    tuples = []
    for adcode, label in filter(lambda t: t[0] is not None, zip(adcodes, labels)):
        addr = ad2addr(adcode)
        if not addr.longitude or not addr.latitude:
            continue
        coordinates[adcode] = (float(addr.longitude), float(addr.latitude))
        tuples.append((adcode, label))

    from pyecharts.charts import Geo
    from pyecharts import options as opts

    geo = Geo(init_opts=opts.InitOpts(width="1200px", height="600px", bg_color="#fff"))

    # 添加坐标
    for adcode, coord in coordinates.items():
        geo.add_coordinate(adcode, coord[0], coord[1])

    # 分组数据
    for label, sub_tuples in itertools.groupby(tuples, operator.itemgetter(1)):
        sub_adcodes_list = list(map(operator.itemgetter(0), sub_tuples))
        value = [1] * len(sub_adcodes_list)
        data = [(adcode, val) for adcode, val in zip(sub_adcodes_list, value)]

        geo = geo.add(
            label,
            data,
            symbol_size=point_size,
        )

    geo = geo.set_global_opts(
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle, pos_left="center"),
        legend_opts=opts.LegendOpts(pos_left="left", pos_top="bottom"),
    )

    geo.render(file_path)
