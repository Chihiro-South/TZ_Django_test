$(() => {

    let sdk = baidubce.sdk;
    let VodClient = sdk.VodClient;

    let config = {
        endpoint: 'http://vod.bj.baidubce.com',
        credentials: {
            ak: 'a03533dabae3483a817d3faf7e244203',
            sk: '51b935e621884fd68912ffc012d8b4a8'
        }
    };
    let client = new VodClient(config);

    let $file = $('up');
    $file.change(function () {
        let video_file = this.files[0];
        console.log(video_file);


        let video_type = video_file.type;
        let title = 'title';
        let desc = 'this is a video';
        let data = new Blob([video_file], {type: video_type});
        let client = new VodClient(config);
        client.createMediaResource(title, desc, data)
        // Node.js中<data>可以为一个Stream、<pathToFile>；在浏览器中<data>为一个Blob对象
            .then(function (response) {
                // 上传完成
                console.log(response.body.mediaId);
            })
            .catch(function (error) {
                console.log(error);
                // 上传错误
//监听progress事件 获取上传进度
                client.on('progress', function (evt) {
                    console.log(evt);
                });

            })
    })
});