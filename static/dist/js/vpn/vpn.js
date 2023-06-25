$(document).ready(function(){
    get_online_user(0)
    get_sun_openvpn_status(FlowChart);
    get_online_user_sun()
    //setInterval(get_online_user,3000,1);
//    setInterval(get_sun_openvpn_status,3000);
});

function user_info_html(user_date) {
	var user_tmp_data = ""
	var user_data_key = ["vpn_name","remove_addr","virtual_addr","sent_bytes","rece_bytes","online_time","nlin","city"]
	//用户名"vpn_name"
	//公网IP"remove_addr"
	//虚拟IP"virtual_addr"
	//发送字节"sent_bytes"
	//接收字节"rece_bytes"
	//在线时长"online_time"
	//国家标识"nlin"
	//城市"city"
	//操作"ope"

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
	button_data = button_data + '<button type="button" value="' + user_data[user_key[0]] + '" class="btn btn-danger vpn-kill">断开连接</button>'
	button_data = button_data + '<button type="button" value="' + user_data[user_key[0]] + '" class="btn btn-danger vpn-active">禁止连接</button>'
	button_data = button_data + "</div></td>"
	tmp_data = tmp_data + button_data
	return tmp_data
}

function FlowChart(legend_data, xAxis_data, series_data) {
  var chartDom = echarts.init(document.getElementById('FlowChartid'));
  var option;
  option = {
      title: {
        text: 'VPN流量'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: legend_data
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      toolbox: {
        feature: {
          saveAsImage: {}
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: xAxis_data
      },
      yAxis: {
        type: 'value'
      },
      series: series_data
  };
  chartDom.setOption(option);
}

function get_online_user(type_date) {
    $.get("/openvpn/get_online_user",function(data,status){
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

function get_sun_openvpn_status(mychart) {
  var legend_data = []
  var xAxis_data = []
  var series_data_tmp = {}
  var series_data_tmp2 = {}
  var series_data = []
  var series_data2 = {}
  $.get("/openvpn/openvpn_flow",function(data,status){
  	data_new = new_brackup_data(data)
  	if (typeof(data_new)=="undefined" || data_new=='' || data_new==null) {
        return
    };
    for (var i=0, u=data_new.length; i < u ; i++) {
        var sent_flow_name = data_new[i]["username"] + '-sent_flow'

        if (!legend_data.includes(sent_flow_name)) {
             legend_data.push(sent_flow_name)
        }
        var rece_flow_name = data_new[i]["username"] + '-rece_flow'
        if (!legend_data.includes(rece_flow_name)) {
             legend_data.push(rece_flow_name)
        }

        var flow_time = data_new[i]["flow_time"]
        if (!xAxis_data.includes(flow_time)) {
             xAxis_data.push(flow_time)
        }
        if (series_data_tmp.hasOwnProperty(sent_flow_name)) {
            series_data_tmp[sent_flow_name].push({"time_data": flow_time, "flow":data_new[i]["sent_flow"]})
        } else {
            series_data_tmp[sent_flow_name] = [{"time_data": flow_time, "flow":data_new[i]["sent_flow"]}]
        }

        if (series_data_tmp.hasOwnProperty(rece_flow_name)) {
            series_data_tmp[rece_flow_name].push({"time_data": flow_time, "flow":data_new[i]["rece_flow"]})
        } else {
            series_data_tmp[rece_flow_name] = [{"time_data": flow_time, "flow":data_new[i]["rece_flow"]}]
        }
    };
    //{user:[{"time_data": flow_time, "rece_flow":20}]}
    var x_index
    var o_index
    var series_data_tmp_legend
    var series_data_tmp_ju
    for (var k in series_data_tmp) {
        o_index = 0
        x_index = 0
        series_data_tmp_legend = series_data_tmp[k].length
        for (var i=0, series_data_tmp_legend; i < series_data_tmp_legend; i++) {
            x_index = xAxis_data.indexOf(series_data_tmp[k][i]["time_data"])
            var x = x_index - o_index - 1
            for (var x_i=0, x; x_i < x; x_i++) {
                if (series_data_tmp2.hasOwnProperty(k)) {
                    series_data_tmp2[k].push("")
                } else {
                    series_data_tmp2[k] = [""]
                }
            }
            if (series_data_tmp2.hasOwnProperty(k)) {
                series_data_tmp2[k].push(series_data_tmp[k][i]["flow"])
            } else {
                series_data_tmp2[k] = [series_data_tmp[k][i]["flow"]]
            }
            o_index = x_index
        }
        series_data_tmp_ju = series_data_tmp_legend - x_index
        for (x_u=0, series_data_tmp_ju; x_u < series_data_tmp_ju; x_u++) {
            if (series_data_tmp2.hasOwnProperty(k)) {
                series_data_tmp2[k].push("")
            } else {
                series_data_tmp2[k] = [""]
            }
        };

    }
    for (var key in series_data_tmp2 ) {
      series_data.push({
        name: key,
        type: 'line',
        //stack: 'Total',
        smooth: true,
        data: series_data_tmp2[key]
      })
    };
    console.log(series_data)
    mychart(legend_data, xAxis_data, series_data);
  });
};

function get_online_user_sun() {
    $.get("/openvpn/user_monitoring/",function(data,status){
        var data_new = new_brackup_data(data)
        if (typeof(data_new)=="undefined" || data_new=='' || data_new==null) {
            return
        }
        $("#Online_users").text(data_new["Online_users"]);
        $("#user_sun").text(data_new["sum_user"]);
  });
};


$('#user-info').on('click','.vpn-kill',function(){
    var user= $(this).val();
    $.ajaxSetup({contentType: "application/json; charset=utf-8"});
    $.post("/openvpn/kill_user/",
    JSON.stringify({"username":user}),
    function(data,status){
        alert(JSON.stringify(data));
    });
});


$('#user-info').on('click','.vpn-active',function(){
    var user= $(this).val();
    console.log(user)
    $.ajaxSetup({contentType: "application/json; charset=utf-8"});
    $.post("/openvpn/user_active/",
    JSON.stringify({"username":user}),
    function(data,status){
        brackup_data(data)
    });
});


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