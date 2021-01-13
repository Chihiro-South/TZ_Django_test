/**
 * Created 蓝羽教学 on 2020/2/24.
 */

$(() => {

    let image_code_uuid = '';   //uuid
    let isMobileFlag = false;
    send_flag = true;

    let $img = $('.form-item .captcha-graph-img img'); // 获取图像
    genre();
    $img.click(genre);

    function genre() {
        image_code_uuid = generateUUID();
        let imageCodeUrl = '/image_code/' + image_code_uuid + '/';

        $img.attr('src', imageCodeUrl)
    }

    // 生成图片UUID验证码
    function generateUUID() {
        let d = new Date().getTime();
        if (window.performance && typeof window.performance.now === "function") {
            d += performance.now(); //use high-precision timer if available
        }
        let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            let r = (d + Math.random() * 16) % 16 | 0;
            d = Math.floor(d / 16);
            return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        return uuid;
    }

    // 手机号验证
    let $mobile = $('#mobile');
    $mobile.blur(fn_check_mobile);

    function fn_check_mobile() {
        isMobileFlag = false;
        let sMobile = $mobile.val();
        if (sMobile === '') {
            message.showError('手机号不能为空！');
            return
        }
        if (!(/^1[3456789]\d{9}$/).test(sMobile)) {
            message.showError('手机号格式错误，请重新输入！')
            return
        }

        $.ajax({
            url: '/mobiles/' + sMobile + '/',
            type: 'GET',
            dataType: 'json'
        })
            .done(function (res) {
                if (res.data.count == 1) {
                    message.showError('手机号已经被注册，请重新输入！')
                } else {
                    message.showSuccess('可以正常使用');
                    isMobileFlag = true;
                    send_flag = true
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！')
            })
    }

    // 短信发送
    let $smsCodeBtn = $('.form-item .sms-captcha');  // 获取按钮元素
    let $imgCodeText = $('#input_captcha'); //  图形码

    $smsCodeBtn.click(function () {
        // 参数验证   手机号    图形文字   uuid
        // 发送ajax
        // 成功和失败回调
        if (send_flag) {
            if (!isMobileFlag) {
                fn_check_mobile();
                return
            }
            // 验证图形
            let text = $imgCodeText.val();
            if (!text) {
                message.showError('请输入图形验证码！');
                return
            }

            if (!image_code_uuid) {
                message.showError('图形UUID为空');
                return
            }

            // 发送ajax
            // 声明参数
            send_flag = false;

            let DataParams = {
                'mobile': $mobile.val(),
                'text': text,
                'image_code_id': image_code_uuid
            };

            $.ajax({
                url: '/sms_code/',
                type: 'POST',
                headers: {
                    "X-CSRFToken": getCookie('csrftoken')
                },
                data: JSON.stringify(DataParams),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
            })
                .done(function (res) {
                    // 响应成功
                    if (res.errno === '0') {
                        message.showSuccess('短信验证码发送成功');
                        // 倒计时
                        let num = 60;
                        let t = setInterval(function () {
                            if (num === 1) {
                                // 清楚定时器
                                clearInterval(t);
                                $smsCodeBtn.html('获取短信验证码');
                                send_flag = true;
                            } else {
                                num -= 1;
                                // 展示倒计时信息
                                $smsCodeBtn.html(num + '秒')
                            }
                        }, 1000);
                    } else {
                        message.showError(res.errmsg);
                        send_flag = true
                    }
                })
                .fail(function () {
                    message.showError('服务器超时，请重试！')
                })


        } else {
            message.showError('短信验证码发送频繁，请耐心等待')
        }


    });

    // 获取cookie
    // get cookie using jQuery
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {

            let cookies = document.cookie.split(';');

            for (let i = 0; i < cookies.length; i++) {

                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

                    break;
                }
            }
        }
        return cookieValue;

    }


});

