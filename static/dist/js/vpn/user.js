$(document).ready(function(){
    get_online_user()
    $(".table-valign-middle").on('click', '.config_download', function(){
        var username = $(this).parents("tr").children("#data-0").text()
        download2(username)
    });
    $(".table-valign-middle").on('click', '.del_uername', function(){
        var username = $(this).parents("tr").children("#data-0").text()
        del_user(username)
    });
//    setInterval(get_sun_openvpn_status,3000);
});

function user_info_html(user_date) {
	var user_tmp_data = ""
	var user_data_key = ["vpn_name","first_name","remove_addr","online_time","nlin","city"]
	//用户名"vpn_name"
	//最近登录公网IP"remove_addr"
	//最近登录在线时长"online_time"
	//国家标识"nlin"
	//最近登录城市"city"
  //操作
	for (var i=0, u=user_date.length; i < u; i++) {
		tmp_data1 = user_info_add(user_data_key,user_date[i])
		user_tmp_data = user_tmp_data + "<tr>" + tmp_data1 + "</tr>"
	};
	return user_tmp_data

}

function user_info_add(user_key,user_data) {
	var tmp_data = ""
	var evalue = ""
	for (var i=0, u=user_key.length; i < u; i++) {
	    evalue = user_data[user_key[i]]
		tmp_data = tmp_data +  '<td id="data-' + i + '">' + evalue + "</td>"
	};
	button_data = '<td><div class="btn-group">'
    button_data = button_data + '<button type="button" class="btn btn-success" data-toggle="modal" data-target="#modal-password">修改密码</button>'
    button_data = button_data + '<button type="button" class="btn btn-danger del_uername">删除用户</button>'
//	button_data = button_data + '<button type="button" class="btn btn-danger">禁止登录</button>'
//  button_data = button_data + '<button type="button" class="btn btn-info">历史登录</button>'
	button_data = button_data + '<button type="button" class="btn btn-default config_download">点击下载VPN配置文件</button>'
	button_data = button_data + "</div></td>"
	tmp_data = tmp_data + button_data
	console.log(tmp_data)
	return tmp_data
}

function get_online_user(type_date) {
    $.get("/openvpn/get_all_user",function(data,status){
        data_new = new_brackup_data(data)
        if (typeof(data_new)=="undefined" || data_new=='' || data_new==null) {
            return
        }
        user_data = user_info_html(data_new)
        $("#user-info").empty();
        $("#user-info").append(user_data);
  });
};


function create_user() {
     $.ajax({
        type: "POST",
        url:"/openvpn/cruate_user/",
        data:$('#create_user').serialize(),// 序列化表单值
        async: false,
        error: function(data) {
            console.log(data)
        },
        success: function(data) {
           console.log(data)
           brackup_data(data)
        }
    });
}

function brackup_data(data) {
    var Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
//      showConfirmButton: False,
        timer: 3000
    });
    if (data == "") {
        $(document).Toasts('create', {
        class: 'bg-warning',
        title: '提示信息',
        subtitle: '关闭',
        body: data["msg"]
      });
    };
   if (data["status"] == "error") {
       $(document).Toasts('create', {
        class: 'bg-warning',
        title: '提示信息',
        subtitle: '关闭',
        body: data["msg"]
      });
   }

   if (data["status"] == "success") {
       $(document).Toasts('create', {
            class: 'bg-success',
            title: '提示信息',
            subtitle: '关闭',
            body: data["msg"]
      });
   };
}
function update_passowd() {
    var new_password = $("#new_password").val()
    var new1_password = $("#new1_password").val()
    if (new_password == "" || new1_password == "" || new_password != new1_password) {
        $(document).Toasts('create', {
            class: 'bg-warning',
            title: '提示信息',
            subtitle: '关闭',
            body: "两次密码不一致,或密码未获取到"
        });
        console.log(new_password, new1_password)
    } else {
         $.ajax({
            type: "POST",
            url:"/openvpn/update_user_pass/",
            data:$('#update-password').serialize(),// 序列化表单值
            async: false,
            error: function(data) {
                console.log(data)
            },
            success: function(data) {
               console.log(data)
               brackup_data(data)
            }
        });
    }
}

function download2(username) {
    var get_url = "/openvpn/config_dow?username=" + username
    $.get(get_url,function(data,status){
    if (data instanceof Object) {
        $(document).Toasts('create', {
        class: 'bg-warning',
        title: '提示信息',
        subtitle: '关闭',
        body: data["msg"]
        });
    } else {
        save_data(data,username)

    }
  });
}

function save_data(data,username) {
    var funDownload = function (content, filename) {
        var eleLink = document.createElement('a');
        eleLink.download = filename;
        eleLink.style.display = 'none';
        // 字符内容转变成blob地址
        var blob = new Blob([content]);
        eleLink.href = URL.createObjectURL(blob);
        // 触发点击
        document.body.appendChild(eleLink);
        eleLink.click();
        // 然后移除
        document.body.removeChild(eleLink);
    };

    if ('download' in document.createElement('a')) {
        // 作为test.html文件下载
        var file_name = username + ".ovpn"
        funDownload(data, file_name);
    } else {
        eleButton.onclick = function () {
            alert('浏览器不支持');
        };
    }
}

function del_user(username) {
    if (username == "") {
        $(document).Toasts('create', {
            class: 'bg-warning',
            title: '提示信息',
            subtitle: '关闭',
            body: "未获取到账户信息"
        });
    } else {
         $.ajax({
            type: "POST",
            url:"/openvpn/delete_user/",
            dataType: "json",
            contentType: "application/json",
            data:JSON.stringify({"user_name":username}),
            async: false,
            error: function(data) {
                console.log(data)
            },
            success: function(data) {
               console.log(data)
               brackup_data(data)

               get_online_user()
            }
        });
    }
}


