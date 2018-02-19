import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from pos.models import Tag, ClothName, Order, OrderItem
from pos.pinyin import PinYin


pinyin = PinYin()
pinyin.load_word()


def home(request):
    return render(request, 'home.html')


def drop(request):
    return render(request, 'drop.html')


def get_tags(request):
    query = request.GET.get('query', '')
    tags = Tag.objects.filter(pinyin__istartswith=query).order_by('-used_count')
    resp = [{'name': tag.pinyin, 'id': tag.name} for tag in tags[:15]]
    return JsonResponse(resp, safe=False)


def get_cloth_names(request):
    query = request.GET.get('query', '')
    names = ClothName.objects.filter(pinyin__istartswith=query).order_by('-used_count')
    resp = [{'name': name.pinyin, 'id': name.name, 'price': name.price} for name in names[:15]]
    return JsonResponse(resp, safe=False)


def update_frequency(request):
    if 'name' in request.GET:
        name = request.GET['name']
        if name:
            price = float(request.GET.get('price', '0'))
            if ClothName.objects.filter(name=name).exists():
                obj = ClothName.objects.get(name=name)
            else:
                obj = ClothName(name=name, pinyin=pinyin.hanzi2shouzimu(name), used_count=0, price=price)
            obj.used_count += 1
            obj.save()
    if 'tags' in request.GET:
        tags = request.GET['tags'].split('；')
        for tag in tags:
            if tag:
                if Tag.objects.filter(name=tag).exists():
                    obj = Tag.objects.get(name=tag)
                else:
                    obj = Tag(name=tag, pinyin=pinyin.hanzi2shouzimu(tag), used_count=0)
                obj.used_count += 1
                obj.save()
    return HttpResponse()


def add_order(request):
    obj = json.loads(request.GET.get('order', ''))
    order = Order(total_price=obj['total'], cash_paid=obj['cash'], card_paid=obj['card'], discount=obj['discount'],
                  discount_percent=obj['discountPercent'], balance=obj['balance'], comment=obj['comment'])
    order.save()
    for item in obj['items']:
        order_item = OrderItem(name=item['name'], tags=item['tags'], unit_price=item['unitPrice'],
                             quantity=item['count'], comment=item['comment'], order=order)
        order_item.save()
    return JsonResponse({'id': order.pk})


def order_detail(request, id):
    order = get_object_or_404(Order, pk=id)
    items = OrderItem.objects.filter(order=order)
    all_washed = all(item.washed for item in items)
    all_picked = all(item.picked for item in items)
    return render(request, 'order.html',
                  {'order': order, 'items': items, 'balance': abs(order.balance), 'all_washed': all_washed,
                   'all_picked': all_picked})


def order_modify(request):
    order = get_object_or_404(Order, pk=request.GET.get('id', 0))
    order_item = get_object_or_404(OrderItem, pk=request.GET.get('item', 0)) if 'item' in request.GET else None
    action = request.GET.get('action', '')
    if action == 'unpick_all':
        for item in order.items.all():
            item.picked = False
            item.washed = False
            item.save()
    elif action == 'pick_all':
        for item in order.items.all():
            item.picked = True
            item.washed = True
            item.save()
    elif action == 'wash_all':
        for item in order.items.all():
            item.picked = False
            item.washed = True
            item.save()
    elif action == 'unpick_item':
        order_item.picked = False
        order_item.washed = False
        order_item.save()
    elif action == 'pick_item':
        order_item.picked = True
        order_item.washed = True
        order_item.save()
    elif action == 'wash_item':
        order_item.picked = False
        order_item.washed = True
        order_item.save()
    order.all_washed = all(item.washed for item in order.items.all())
    order.all_picked = all(item.picked for item in order.items.all())
    order.save()
    return HttpResponse()


def order_delete(request, id):
    order = get_object_or_404(Order, pk=id)
    order.delete()
    return redirect(reverse('home'))
