#!/usr/bin/env python3
"""Price candidate gate for EEMON. No scraping or automatic publishing.

Input represents an observation made through a source explicitly permitted by that
source's terms. Structural validation is NOT independent seller verification.
Unknown shipping, stale data, non-available stock or unequal SKUs never enter ranking.
"""
import argparse
import datetime as dt
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

JST=dt.timezone(dt.timedelta(hours=9))
DEFAULT_FRESHNESS_HOURS=24
MAX_PRICE_YEN=50_000_000

class ValidationError(ValueError): pass

def safe_url(value: str) -> str:
    if not isinstance(value, str) or len(value)>2048:raise ValidationError('URLが無効')
    u=urlsplit(value)
    if u.scheme != 'https' or not u.hostname or u.username or u.password or u.fragment:
        raise ValidationError('httpsの公開URLのみ許可')
    host=u.hostname.lower()
    if host=='localhost' or host.endswith('.local') or not '.' in host:raise ValidationError('ローカルURLは禁止')
    try:
        ipaddress.ip_address(host)
        raise ValidationError('IP直指定は禁止')
    except ValueError as exc:
        if str(exc)=='IP直指定は禁止':raise
    return value

def int_yen(value, field, *, minimum=0):
    if type(value) is not int or not minimum<=value<=MAX_PRICE_YEN:raise ValidationError(f'{field}: 整数円のみ')
    return value

def stamp(value):
    if not isinstance(value,str):raise ValidationError('確認時刻がない')
    try: t=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: raise ValidationError('確認時刻の形式が違う')
    if t.tzinfo is None:raise ValidationError('確認時刻はタイムゾーン必須')
    return t.astimezone(dt.timezone.utc)

def compare(payload, now=None, freshness_hours=DEFAULT_FRESHNESS_HOURS):
    now=now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:raise ValueError('now requires timezone')
    if payload.get('demo_data') is True:raise ValidationError('デモ価格の本番取込は禁止')
    records=payload.get('observations')
    if not isinstance(records,list):raise ValidationError('observations must be list')
    accepted=[]; excluded=[]; already=set()
    for idx,raw in enumerate(records):
        try:
            if not isinstance(raw,dict):raise ValidationError('レコード形式が違う')
            product_key=raw.get('product_key'); listing_key=raw.get('listing_key')
            if not isinstance(product_key,str) or not 3<=len(product_key)<=100:raise ValidationError('商品型番キー必須')
            if not isinstance(listing_key,str) or not 3<=len(listing_key)<=120:raise ValidationError('販売ページキー必須')
            if any(ch.isspace() for ch in product_key):raise ValidationError('商品型番キーの空白は禁止')
            if not isinstance(raw.get('product_name'),str) or not raw['product_name'].strip():raise ValidationError('商品名必須')
            if not isinstance(raw.get('shop_name'),str) or not raw['shop_name'].strip():raise ValidationError('店舗名必須')
            if raw.get('stock')!='available':raise ValidationError('在庫確認なし')
            if raw.get('verification')!='human_verified_official_page':raise ValidationError('目視の原典確認が必要')
            if not isinstance(raw.get('verified_by'),str) or not raw['verified_by'].strip():raise ValidationError('確認担当の記録が必要')
            item_url=safe_url(raw.get('item_url'))
            evidence_url=safe_url(raw.get('evidence_url'))
            price=int_yen(raw.get('price_jpy'),'price_jpy',minimum=1)
            shipping=int_yen(raw.get('shipping_jpy'),'shipping_jpy')
            checked=stamp(raw.get('checked_at'))
            age=(now-checked).total_seconds()
            if age < -300:raise ValidationError('未来の確認時刻')
            if age > freshness_hours*3600:raise ValidationError('確認期限切れ')
            # Currency, variant, tax, exclusions must be explicit.
            if raw.get('currency')!='JPY' or raw.get('tax_included') is not True:
                raise ValidationError('税込JPYでの確認が必要')
            if raw.get('variant_key')!=product_key:
                raise ValidationError('同一SKU・色・仕様の検査不一致')
            key=(product_key,listing_key)
            if key in already:raise ValidationError('商品・販売ページの重複')
            already.add(key)
            accepted.append({'product_key':product_key,'product_name':raw['product_name'].strip(),
             'listing_key':listing_key,'shop_name':raw['shop_name'].strip(),
             'item_url':item_url,'evidence_url':evidence_url,
             'total_jpy':price+shipping,'price_jpy':price,'shipping_jpy':shipping,
             'checked_at':checked.isoformat(),'verified_by':raw['verified_by'].strip(),
             'verification':'SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED'})
        except ValidationError as e:
            excluded.append({'index':idx,'product_key':raw.get('product_key') if isinstance(raw,dict) else None,'reason':str(e)})
    groups={}
    for item in accepted:groups.setdefault(item['product_key'],[]).append(item)
    summary=[]
    for key,values in sorted(groups.items()):
        values.sort(key=lambda o:(o['total_jpy'],o['shop_name']))
        summary.append({'product_key':key,'product_name':values[0]['product_name'],
         'scope':'入力された同一SKUの、条件を満たす店舗のみ。全国最安値ではありません。',
         'offer_count':len(values),'offers':values})
    return {'generated_at':now.astimezone(JST).isoformat(timespec='seconds'),
            'verification':'SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED',
            'summary':summary,'excluded':excluded,
            'message':f'{len(accepted)}件表示候補／{len(excluded)}件除外。公開前に原典を再確認してください。'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--now',type=str,help='QA用固定時刻。ISO8601 timezone required')
    args=parser.parse_args()
    payload=json.loads(args.input.read_text('utf8'))
    now=stamp(args.now) if args.now else None
    result=compare(payload,now)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f"VALIDATED:{sum(x['offer_count'] for x in result['summary'])} EXCLUDED:{len(result['excluded'])}")
    return 0
if __name__=='__main__':raise SystemExit(main())