from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

from myadmin.models import Types, Goods, Orders
from PIL import Image

import time, json, os


# ==================后台商品类别管理======================
def typeindex(request):
    """浏览商品类别信息:
    """
    # 执行数据查询, 并把结果放到模板中
    lst = Types.objects.extra(select={'_has': 'concat(path, id)'}).order_by(
        '_has')
    # 遍历查询结果，为每个结果对象追加一个pname属性，目的用于缩进标题
    for ob in lst:
        ob.pname = '. . . ' * (ob.path.count(',') - 1)
        # print(lst[0].__dict__)
    context = {"typeslist": lst}
    return render(request, 'myadmin/type/index.html', context)


def typeadd(request, tid):
    """商品类别添加表单"""
    # 获取父类别信息,若没有默认为根类别信息
    if tid == '0':
        context = {'pid': 0, 'path': '0,', 'name': '根类别'}
    else:
        ob = Types.objects.get(id=tid)
        context = {
            'pid': ob.id, 'path': ob.path + str(ob.id) + ',', 'name': ob.name
        }
    return render(request, 'myadmin/type/add.html', context)


def typeinsert(request):
    """添加商品类别"""
    try:
        ob = Types()
        ob.name = request.POST['name']
        ob.pid = request.POST['pid']
        ob.path = request.POST['path']
        ob.save()
        context = {'info': '添加成功！'}
    except:
        context = {'info': '添加失败！'}

    return render(request, "myadmin/info.html", context)


def typedel(request, tid):
    """删除商品类别"""
    try:
        # 获取被删除商品的子列表信息, 若有数据, 就禁止删除当前类别
        row = Types.objects.filter(pid=tid).count()
        if row > 0:
            context = {'info': '删除失败:此类别下还有子类'}
            return render(request, 'myadmin/info.html', context)

        ob = Types.objects.get(id=tid)
        ob.delete()
        context = {'info': '删除成功!'}
    except:
        context = {'info': '删除失败!'}

    return render(request, 'myadmin/info.html', context)


def typeedit(request, tid):
    """商品类别修改表单"""
    try:
        ob = Types.objects.get(id=tid)
        context = {'type': ob}
        return render(request, "myadmin/type/edit.html", context)
    except:
        context = {'info': '没有找到要修改的信息！'}
    return render(request, "myadmin/info.html", context)


def typeupdate(request):
    """修改商品类别信息"""
    try:
        ob = Types.objects.get(id=tid)
        ob.name = request.POST['name']
        ob.save()
        context = {'info': '修改成功!'}
    except:
        context = {'info': '修改成功!'}
    return render(request, 'myadmin/info.html', context)


# =================后台商品信息管理======================
def goodsindex(request, pIndex=1):
    """商品信息页面"""
    # 执行数据查询，并放置到模板中
    lst = Goods.objects.all()

    for ob in lst:
        ty = Types.objects.get(id=ob.typeid)
        ob.typename = ty.name  # 判断并封装搜索条件

    # 传入数据和页大小来创建分页对象
    p = Paginator(lst, 4)
    # 判断页号没有值时初始化为1
    if pIndex == '':
        pIndex = '1'
    pIndex = int(pIndex)  # 类型转换int
    list2 = p.page(pIndex)  # 获取当前页数据
    plist = p.page_range  # 获取页码信息
    # 封装分页信息
    context = {'goodslist': list2, 'plist': plist, 'pIndex': pIndex}
    return render(request, "myadmin/goods/index.html", context)


def goodsadd(request):
    """
    商品信息添加表单

    :param request:
    :return:
    """
    # 获取商品类别信息
    lst = Types.objects.extra(select={'_has': 'concat(path,id)'}).order_by(
        '_has')
    context = {'typelist': lst}
    return render(request, "myadmin/goods/add.html", context)


def goodsinsert(request):
    """添加商品信息"""
    try:
        # 判断并执行图片上传,缩放等处理
        myfile = request.FILES.get("pic", None)
        if not myfile:
            return HttpResponse("没有上传文件信息")

        # 以时间戳命名一个新图片名称
        filename = str(time.time()) + "." + myfile.name.split('.').pop()
        destination = open(os.path.join("./static/goods/", filename), 'wb+')
        for chunk in myfile.chunks():
            destination.write(chunk)
        destination.close()
        # 执行图片缩放
        im = Image.open("./static/goods/" + filename)
        # 缩放到375*375
        im.thumbnail((375, 375))
        # 把缩放后的图片以jpeg格式保存
        im.save("./static/goods/" + filename, 'jpeg')
        # 缩放到220
        im.thumbnail((220, 220))
        # 把缩放后图片以jpeg格式保存
        im.save("./static/goods/m_" + filename, 'jpeg')
        # 缩放为100
        im.thumbnail((100, 100))
        # 把缩放后图片以jpeg格式保存
        im.save("./static/goods/s_" + filename, 'jpeg')

        # 获取商品信息并执行添加
        ob = Goods()
        ob.goods = request.POST['goods']
        ob.typeid = request.POST['typeid']
        ob.company = request.POST['company']
        ob.price = request.POST['price']
        ob.store = request.POST['store']
        ob.descr = request.POST['descr']
        ob.picname = filename
        ob.state = 1
        ob.addtime = time.time()
        ob.save()
        context = {'info': '添加成功! '}
    except:
        context = {'info': '添加失败! '}
    return render(request, "myadmin/info.html", context)


def goodsdel(request, gid):
    """删除商品信息"""
    try:
        # 获取被删除商品信息量,先删除对应的图片
        ob = Goods.objects.get(id=gid)
        if ob.state == 1:
            # 执行图片删除
            os.remove("./static/goods/" + ob.picname)
            os.remove("./static/goods/m_" + ob.picname)
            os.remove("./static/goods/s_" + ob.picname)
            # 执行商品信息的删除
            ob.delete()
            context = {'info': '删除成功!'}
        else:
            context = {'info': '此状态不能删除!'}
    except:
        context = {'info': '删除失败!'}
    return render(request, "myadmin/info.html", context)


def goodsedit(request, gid):
    """商品信息编辑表单"""
    try:
        # 获取要编辑的信息
        ob = Goods.objects.get(id=gid)
        # 获取商品的类别信息
        lst = Types.objects.extra(select={'_has': 'concat(path,id)'}).order_by(
            '_has')
        # 放置信息加载模板
        context = {"typelist": lst, 'goods': ob}
        return render(request, "myadmin/goods/edit.html", context)
    except:
        context = {'info': '没有找到要修改的信息！'}
    return render(request, "myadmin/info.html", context)


def goodsupdate(request, gid):
    """修改商品信息"""
    try:
        b = False
        oldpicname = request.POST['oldpicname']

        if None != request.FILES.get("pic"):
            myfile = request.FILES.get('pic', None)
            if not myfile:
                return HttpResponse("没有上传文件信息!")

            # 以时间戳命名一个新图片名称
            filename = str(time.time()) + "." + myfile.name.split('.').pop()
            destination = open(os.path.join("./static/goods/", filename), 'wb+')
            for chunk in myfile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            # 执行图片缩放
            im = Image.open("./static/goods/" + filename)
            # 缩放到375*375:
            im.thumbnail((375, 375))
            # 把缩放后的图像用jpeg格式保存:
            im.save("./static/goods/" + filename, 'jpeg')
            # 缩放到220*220:
            im.thumbnail((220, 220))
            # 把缩放后的图像用jpeg格式保存:
            im.save("./static/goods/m_" + filename, 'jpeg')
            # 缩放到220*220:
            im.thumbnail((100, 100))
            # 把缩放后的图像用jpeg格式保存:
            im.save("./static/goods/s_" + filename, 'jpeg')
            b = True
            picname = filename
        else:
            picname = oldpicname

        ob = Goods.objects.get(id=gid)
        ob.goods = request.POST['goods']
        ob.typeid = request.POST['typeid']
        ob.company = request.POST['company']
        ob.price = request.POST['price']
        ob.store = request.POST['store']
        ob.descr = request.POST['descr']
        ob.picname = picname
        ob.state = request.POST['state']
        ob.save()
        context = {'info': '修改成功！'}
        if b:
            os.remove("./static/goods/m_" + oldpicname)  # 执行老图片删除
            os.remove("./static/goods/s_" + oldpicname)  # 执行老图片删除
            os.remove("./static/goods/" + oldpicname)  # 执行老图片删除
    except:
        context = {'info': '修改失败！'}
        if b:
            os.remove("./static/goods/m_" + picname)  # 执行新图片删除
            os.remove("./static/goods/s_" + picname)  # 执行新图片删除
            os.remove("./static/goods/" + picname)  # 执行新图片删除
    return render(request, "myadmin/info.html", context)


# ==============后台订单信息管理======================
def ordersindex(request):
    """后台订单信息表单"""
    list1 = Orders.objects.all()
    context = {'orderslist': list1}
    return render(request, "myadmin/orders/index.html", context)


def ordersedit(request, oid):
    """
    订单信息更改表单

    :param request:
    :param oid: 订单id
    :return:
    """
    ob = Orders.objects.get(id=oid)
    context = {'orders': ob}
    return render(request, "myadmin/orders/edit.html", context)


def ordersupdate(request, oid):
    """
    更改订单状态

    :param request:
    :param oid: 订单id
    :return:
    """
    try:
        ob = Orders.objects.get(id=oid)
        ob.status = request.POST['status']
        ob.save()
        context = {'info': '修改成功!'}
    except:
        context = {'info': '修改成功!'}
    return render(request, 'myadmin/info.html', context)
