$(document).ready(function(){
    get_online_user("","",0)
    $("#vpn_login_log_get").click(function(){
        get_show_time_rage();
    });
    //$("#vpn_login_log_get").click(get_show_time_rage())


    //setInterval(get_online_user,3000,1);
//    setInterval(get_sun_openvpn_status,3000);
});

function user_info_html(user_date) {
	var user_tmp_data = ""
	var user_data_key = ["vpn_name","remove_addr","virtual_addr","online_time","offline_time","login_type"]
	//用户名"vpn_name"
	//公网IP"remove_addr"
	//虚拟IP"virtual_addr"
	//登录时间"sent_bytes"
	//下线时间"rece_bytes"
	//认证状态"online_time"
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
		tmp_data = tmp_data +  "<td>" + evalue + "</td>"
	};
	button_data = '<td><div class="btn-group">'
	button_data = button_data + "</div></td>"
	tmp_data = tmp_data + button_data
	return tmp_data
}

function get_online_user(time_std,time_sed,type_date) {
    var url = "/openvpn/login_log_data?time_std=" + time_std + "&time_sed=" + time_sed
    $.get(url,function(data,status){
        var data_new = new_brackup_data(data)
        if (typeof(data_new)=="undefined" || data_new=='' || data_new==null) {
            return
        }
        user_data = user_info_html(data_new)
        if (type_date == 0 ) {
            $("#user-info").append(user_data);
        };
        if (type_date == 1 ) {
            $("#user-info").empty();
            $("#user-info").append(user_data);
        };
  });
};

function set_input_border(input_id,color_v) {
    if (color_v == 1) {
        var color_data = "1px solid #ff0000"
    } else {
        var color_data = "1px solid rgb(206, 212, 218)"
    }
    $("#" + input_id).css("border",color_data)
}

function get_show_time_rage() {
    var time_std = $("#time_std").val();
    var time_sed = $("#time_sed").val();

    var panduan = 1
    var sed_regex = /^[0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}$/g
    if (!!time_sed) {
        if (sed_regex.test(time_sed)) {
            set_input_border("time_sed",0)
        } else {
            set_input_border("time_sed",1)
            panduan = 0
             console.log("2",time_sed);
        }
    } else {
        set_input_border("time_sed",1)
        panduan = 0
    };

    var std_regex = /^[0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}$/g
    if (!!time_std) {
       if (std_regex.test(time_std)) {
           console.log("3",time_std);
           set_input_border("time_std",0)
       } else {
           console.log("2",time_std);
           set_input_border("time_std",1)
           panduan = 0
       }
    } else {
        set_input_border("time_std",1)
        panduan = 0
    };

    if (panduan == 1) {
        get_online_user(time_std, time_sed,1)
    }
}








