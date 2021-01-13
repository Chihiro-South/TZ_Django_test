$(function () {
    let $login = $('.form-contain');
    $login.submit(function (e) {
        e.preventDefault();
        let User_Tel = $('input[name=user_tel]').val();
        alert(User_Tel);
        if (User_Tel === '') {
            message.showError('用户名不能为空！')
            return
        }
        // 密码验证

        let old_Password = $('input[name=old_password]').val();
        alert(old_Password);
        if (!old_Password) {
            message.showError('密码不能为空!')
            return
        }
        let new_Password = $('input[name=new_password]').val();
        alert(new_Password);
        if (!new_Password) {
            message.showError('密码不能为空!')
            return
        }
        if (new_Password.length < 6 || new_Password.length > 20) {
            message.showError('密码长度需要在6-20之间');
            return
        }



        // g构造参数
        let sData = {
            'user_tel': User_Tel,
            'old_password': old_Password,
            'new_password': new_Password
        };



        $.ajax({
            url: '/user/changepwd/',
            type: 'POST',
            headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
            data: JSON.stringify(sData),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
        })
            .done(function (res) {
                alert('.done')
                if (res.errno === "0") {
                    message.showSuccess('密码修改成功！');
                    setTimeout(function () {
                        window.location.href = '/';
                    }, 1500)
                } else {
                    message.showError('密码修改失败！')
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
