function readydo_info()
{
	init_show()
}


function readydo_ope()
{
	//init_show()

	button_click()

}

function button_click()
{
	$("#btn_dv").click(create_br_closure('dv'))
	$("#btn_qa").click(create_br_closure('qa'))
	$("#btn_hf").click(create_br_closure('hf'))
	$("#btn_rl").click(create_br_closure('rl'))
	$("#btn_dp").click(create_br_closure('dp'))

	$("#btn_merge_qa").click(merge_br_closure('qa'))
	$("#btn_merge_dv").click(merge_br_closure('dv'));
	$("#btn_merge_ms").click(merge_br_closure('ms'));

}

function merge_br_closure(tp)
{
	var input_merge_info = "#input_merge_info_" + tp
	var input = "#input_merge_" + tp
	var merge_list = "#input_merge_list_" + tp
	var div = '#div_res_merge_' + tp



	return function()
		{
			$(div).html('<pre>loading...</pre>')
			var base = $(input).val()
			var mlist = $(merge_list).val()

			uri = "/git/merge/" + tp
			$.post(uri, {base_br: base, merge_list: mlist, merge_info: $(input_merge_info).val()}, merge_br_cb_closure(div))

		}

}

function merge_br_cb_closure(user_data)
{
	return function(data, status)
		{

			var obj = eval('(' + data + ')')
			var htm = ''
			if (obj.code != 0) {
				htm = err_show(obj)
			} else {
				merge_info = obj.res.merge
				push_info = obj.res.push
				htm = '<pre>'
				htm += '[merge_info]\n' + merge_info
				htm += '\n[push_info]\n' + push_info
				htm += '</pre>'
			}


			$(user_data).html(htm)

		}
}


function create_br_closure(tp)
{
	var input_base = "#input_base_" + tp
	var input = "#input_" + tp
	var div = '#div_res_' + tp

	return function()
		{
			ib = $(input_base).val()
			$(div).html('<pre>loading...</pre>')
			br = $(input).val()
			uri = "/git/branch/" + tp + "/" + br
			$.post(uri, {base: ib}, create_br_cb_closure(div))

		}
}


function err_show(obj)
{

	var htm = ''
	htm = '<pre>'
	htm += 'code:' + obj.code + '\n'
	htm += 'cmd:' + obj.cmd + '\n'
	htm += 'err:' + obj.err + '\n'
	htm += '</pre>'
	return htm

}

function create_br_cb_closure(user_data)
{
	return function(data, status)
		{
			var obj = eval('(' + data + ')')
			var htm = ''
			if (obj.code != 0) {
				htm = err_show(obj)
			} else {
				htm = '<pre>' + obj.res + '</pre>'
			}


			$(user_data).html(htm)

		}
}

function init_show()
{
	/*
	$.get("/git/stat/merge/qa", qa_merge_stat)
	$.get("/git/stat/merge/dev", dev_merge_stat)
	$.get("/git/stat/merge/deploy", deploy_merge_stat)
	$.get("/git/stat/merge/master", master_merge_stat)
	*/

	$.get("/git/stat/merge", merge_stat_all)
}

function merge_stat_all(response, status, xhr)
{
	//$('#div1').text(response)
	//return

	var obj = eval('(' + response + ')')
	var htm = ''
	if (obj.code != 0) {
		htm = err_show(obj)
		$('#div1').html(htm)

		return
	}

	obj = obj.res



    var dev_stat = obj.dev_stat
    var cmp_qa = obj.cmp_qa
    var cmp_dev = obj.cmp_dev
    var nomerge_dev_stat = obj.nomerge_dev_stat
    var nomerge_dep_stat = obj.nomerge_dep_stat

	htm += '<h3>没有合并入master的release</h3>'
	htm += '<hr/>'
	for (var e in nomerge_dep_stat) {
		var cb = nomerge_dep_stat[e]
		htm += '<h4>' + e + '</h4>'
		htm += '<pre>'
		for (var c in cb) {
			htm += '\n[' + c + ']\n'
			htm += cb[c] + '\n'
		}
		htm += '</pre>'

	}


	htm += '<h3>没有合并入release的develop</h3>'
	htm += '<hr/>'
	for (var e in nomerge_dev_stat) {
		var cb = nomerge_dev_stat[e]
		htm += '<h4>' + e + '</h4>'
		htm += '<pre>'
		for (var c in cb) {
			htm += '[' + c + ']\n'
			htm += cb[c]
		}
		htm += '</pre>'

	}




	htm += '<h3>qa/*已经并入的开发分支</h3>'
	htm += '<hr/>'
	for (var e in cmp_qa) {
		var cb = cmp_qa[e]
		htm += '<h4>' + e + '</h4>'
		htm += '<pre>'
		for (var i = 0; i < cb.length; i++) {
			htm += '[' + cb[i] + ']\n'
		}
		htm += '</pre>'
	}


	htm += '<h3>develop已经并入的开发分支</h3>'
	htm += '<hr/>'
	for (var e in cmp_dev) {
		var cb = cmp_dev[e]
		htm += '<h4>' + e + '</h4>'
		htm += '<pre>'
		for (var i = 0; i < cb.length; i++) {
			htm += '[' + cb[i] + ']\n'
		}
		htm += '</pre>'
	}



	htm += '<h3>当前开发分支合并状态</h3>'
	htm += '<hr/>'

	for (var e in dev_stat) {
		var cb = dev_stat[e]
		htm += '<h4>' + e + '</h4>'
		htm += '<pre>'
		var ismerge = false
		for (var i = 0; i < cb.length; i++) {
			htm += '[' + cb[i] + ']'
			ismerge = true
		}
		if (!ismerge) {
			htm += '没有合并'
		}
		htm += '</pre>'
	}



	//===========================


	$('#div1').html(htm)
}


function qa_merge_stat(response, status, xhr)
{
	merge_stat(response, status, xhr, '#div1')
}

function dev_merge_stat(response, status, xhr)
{
	merge_stat(response, status, xhr, '#div2')
}

function deploy_merge_stat(response, status, xhr)
{
	merge_stat(response, status, xhr, '#div3')
}


function master_merge_stat(response, status, xhr)
{
	merge_stat(response, status, xhr, '#div4')
}


function merge_stat(response, status, xhr, id)
{

	var obj = eval('(' + response + ')')
	var htm = ''

	for (var e in obj) {
		htm += '<h3>' + e + ': 已经并入当前分支的功能' + '</h3>'
		htm += '<hr/>'
		for (var c in obj[e]) {
			var ifo = obj[e][c]
			if (0 == ifo.length)
				htm += '<pre>' + c + '</pre>'

			//htm += '<pre>' + ifo + '</pre>'
		}

	}

	$(id).html(htm)
}


function init_get(data, status)
{

}
