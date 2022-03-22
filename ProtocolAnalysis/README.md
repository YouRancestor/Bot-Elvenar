# 协议分析
- 使用登陆后的 cookie 访问 en0.envenar.com 可直接登陆
- Cookie 的拼接方法：
    - en.elvenar.com
        - PHPSSIONID: 从HTTP GET url 的 response获得，如果没有则获得一个新的，如返回了一个新的，则下次请求应使用新的。
        - XSRF-TOKEN: 从HTTP GET url 的 response获得
        - ig_conv_last_site=https://en0.elvenar.com/web/error/no-session
        - device_view=full
        - metricsUvId: 从HTTP GET url 的 response获得
        - portal_ref_url=https://en0.elvenar.com/
        - portal_ref_session=1
        - portal_tid: 从HTTP GET url 的 response获得
        - portal_data=portal_tid=${portal_tid}&portal_ref_session=1&portal_ref_url=https://en0.elvenar.com/ ，上面三个portal_*字段的拼接形如“portal_data=portal_tid=1647811836859-18715&portal_ref_session=1&portal_ref_url=https://en0.elvenar.com/”
    - en0.elvenar.com
        - _mid: 未知，可通过模拟浏览器点击登陆按钮，等待页面加载后获得。
        - cid: 未知，同上。
        - ig_conv_last_site=https://en0.elvenar.com/web/error/no-session
        - metricsUvId: 继承自 en.elvenar.com
        - portal_*: 继承自 en.elvenar.com
    - en2.elvenar.com
        - metricsUvId: 继承自 en.elvenar.com
        - ig_conv_last_site=https://en0.elvenar.com/web/glps
        - cid: 由 /login/play 响应获得
        - sid: 由game页面获得，base64编码，解码后形如qUWb7-zw13z4Jw5。
        - req_page_info: 形如 game_v1 ，由/login/play响应获得。
        - start_page_type=game ，由req_page_info拆分获得
        - start_page_version=v1 ，由req_page_info拆分获得
- 模拟浏览器登陆后，位于 https://en0.elvenar.com/web/glps 页面。携带 cookie POST 请求 https://en0.elvenar.com/web/login/play 得到响应——含口令参数的en2的url，GET 请求该url（这里有一个cookie sid未知，可能不需要，是后边获取的），获得302响应重定向至 https://en2.elvenar.com/game 页面。
- /game 页面返回内容中找 json_gateway_url 和 socket_gateway_url 以及 sid 进行 base64解码后，分别得到 POST 请求的 url （形如//en2.elvenar.com/game/json?h=37dca9b3520）和 websockt 的 url （wss://en2.elvenar.com/ws/stomp）以及en2的cookie sid。
- 发送POST请求时，需要将请求做摘要处理，加在JSON数据的前面。
    - 摘要算法： encodedRequest:function(a)
    ```
        var b = json_gateway # //en2.elvenar.com/game/json?h=bf76b6be0f5
        var d = b.lastIndexOf('?h=') + 3;          # 27 + 3 = 30 
        var b = Sa.substr(b, d, b.length - d)      # b.substr(30, 41 - 30) 即 bf76b6be0f5
        jsonstr = JSON.stringify(request)          # "[{\"requestId\":50,\"requestMethod\":\"clearIndicator\",\"requestClass\":\"IndicatorsService\",\"requestData\":[\"\",\"messages\"],\"__clazz__\":\"ServerRequestVO\"}]"  注意'\'是显示时加上去的实际内容不含'\'
        key = "MAW#YB*y06wqz$kTOE"          # https://oxen.innogamescdn.com/cache/elvenar-ax3-release-466d7991ee77468b703de2011ce97360.js 这个脚本里 get_key() 的返回值 搜 get_key:function(){return" 这个脚本在 /game 页面里搜elvenar-ax3-release可以找到具体文件名
        Request_data = Xha.hash(b + key + jsonstr).substr(0, 10) + jsonstr   # hash算法是 MD5 32位 小写 取前10字节 例如 20f0b5d67e
    ```
    

    
