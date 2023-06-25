$(document).ready(function(){
    $("#logout").click(function(){
        $(window).attr('location',"/openvpn/logout");
    });
});

function new_brackup_data(data) {
   if (data == "") {
       $(document).Toasts('create', {
       class: 'bg-warning',
       title: '提示信息',
       subtitle: '关闭',
       body: data["msg"]
       });
       console.log(1)
      return
   };
   if (data["status"] == "error") {
       $(document).Toasts('create', {
        class: 'bg-warning',
        title: '提示信息',
        subtitle: '关闭',
        body: data["msg"]
      });
      console.log(2)
      return
   };
   if (data["status"] == "success") {
       return data["msg"]
   };
};
