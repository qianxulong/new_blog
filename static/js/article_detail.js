 $(".action").on('click', function () {

     if($(".info").attr("username"))
     {

         var is_click = $(this).hasClass("diggit");
         var article_id = $(".info").attr("article_id");
        $.ajax(
            {
                url: '/app01/up_down/',
                type: 'post',
                data: {
                    is_click: is_click,
                    article_id: article_id,
                    csrfmiddlewaretoken:$("[name='csrfmiddlewaretoken']").val()
                },
                success:function(data){
                    if(data.status) {
                        if (is_click) {
                            var up_count = $("#digg_count").text();
                            up_count = parseInt(up_count) + 1;
                            $("#digg_count").text(up_count);
                        } else {
                            var down_count = $("#bury_count").text();
                            down_count = parseInt(down_count) + 1;
                            $("#bury_count").text(down_count);
                        }
                    }
                    else{
                            if(data.first_action){
                                $(".diggword").text("你已经点赞过");
                            } else{
                                $(".diggword").text("你已经踩过");
                            }
                             setTimeout(function () {
                                 $("#digg_tips").html("")
                                 },1000)
                    }
                }
        })
     }
     else{
         location.href="/login/"
     }

        })

//  $("#div_digg .action").click(function () {
//     if ($(".info").attr("username")) {
//
//
//         // 点赞或踩灭
//         var is_up = $(this).hasClass("diggit");
//         var article_id = $(".info").attr("article_id");
//         console.log(is_up,article_id)
//         $.ajax({
//             url: "/app01/up_down/",
//             type: "post",
//             data: {
//                 is_up: is_up,
//                 article_id: article_id,
//                 csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
//             },
//             success: function (data) {
//                 console.log(data);
//
//
//                 if (data.state) {// 赞或者灭成功
//
//                     if (is_up) {
//                         var val = $("#digg_count").text();
//                         val = parseInt(val) + 1;
//                         $("#digg_count").text(val);
//                     } else {
//                         var val = $("#bury_count").text();
//                         val = parseInt(val) + 1;
//                         $("#bury_count").text(val);
//                     }
//                 }
//                 else {    // 重复提交
//
//                     if (data.fisrt_action) {
//                         $("#digg_tips").html("您已经推荐过");
//                     } else {
//                         $("#digg_tips").html("您已经反对过");
//                     }
//
//                     setTimeout(function () {
//                         $("#digg_tips").html("")
//                     }, 1000)
//
//                 }
//
//             }
//         })
//
//
//     }
//     else {
//         location.href = "/login/"
//     }
//
//
// });