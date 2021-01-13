$(function () {
    let $login = $('.form-contain');

    $login.submit(function (e) {
        e.preventDefault();
        let sUsername = $('input[name=telephone]').val();
        // alert(sUsername);
        if (sUsername === '') {
            message.showError('用户名不能为空！')
            return
        }

        if (!(/^[\u4e00-\u9fa5\w]{5,20}$/.test(sUsername))) {
            message.showError('请输入5-20位字符的用户名')
            return
        }
        // 密码验证

        let sPassword = $('input[name=password]').val();
        // alert(sPassword);
        if (!sPassword) {
            message.showError('密码不能为空!')
            return
        }
        if (sPassword.length < 6 || sPassword.length > 20) {
            message.showError('密码长度需要在6-20之间');
            return
        }

        let status = $("input[type='checkbox']").is(':checked');

        // g构造参数
        let sData = {
            'user_account': sUsername,
            'password': sPassword,
            'remember': status
        };
        for (i=0;i<sData.length;i++){alert(sData[i]);}


        $.ajax({
            url: '/user/login/',
            type: 'POST',
            headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
            data: JSON.stringify(sData),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
        })
            .done(function (res) {
                if (res.errno === '0') {
                    message.showSuccess('贵宾，恭喜您登录成功！');
                    setTimeout(function () {
                        window.location.href = '/';
                    }, 1500)
                } else {
                    message.showError(res.errmsg)
                }

            })
            .fail(function () {
                message.showError('服务器超时，请重试！')
            })

    });
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
