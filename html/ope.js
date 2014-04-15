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
	$("#btn_merge_ms2").click(merge_br_closure('ms2'));
	$("#btn_merge_hf").click(merge_br_closure('hf'));



	$("#btn_check_qa").click(check_merge_br_closure('qa'))
	$("#btn_check_dv").click(check_merge_br_closure('dv'));
	$("#btn_check_ms").click(check_merge_br_closure('ms'));
	$("#btn_check_ms2").click(check_merge_br_closure('ms2'));
	$("#btn_check_hf").click(check_merge_br_closure('hf'));

}

function check_merge_br_closure(tp)
{
	var input = "#input_merge_" + tp
	var merge_list = "#input_merge_list_" + tp
	var div = '#div_res_merge_' + tp



	return function()
		{
			$(div).html('<pre>loading...</pre>')
			var base = $(input).val()
			var mlist = $(merge_list).val()

			uri = "git/mergecheck/" + tp
			$.post(
				   uri,
	               {base_br: base, merge_list: mlist},
				   check_merge_br_cb_closure(div)
				   )

		}

}


function check_merge_br_cb_closure(user_data)
{
	return function(data, status)
		{

			var obj = eval('(' + data + ')')
			var htm = ''
			if (obj.code != 0) {
				htm = err_show(obj)
			} else {
				htm = '<pre>'
				var check_stat = obj.res.stat
				var heads = obj.res.heads
				for (var e in check_stat) {
					var cb = check_stat[e]
					htm += base_br_show(e, heads)

					for (var c in cb) {
						htm += cmp_br_show(c, heads) + '\n'
						if (cb[c].length == 0) {
							htm += '没有未合并的内容\n'
						} else {
							for (var k in cb[c]) {
								htm += gitweb_commit(cb[c][k][0], cb[c][k][2]) + '\n'
							}
							//htm += cb[c] + '\n'
						}
					}

				}
				htm += '</pre>'

			}

			$(user_data).html(htm)

		}
}



function merge_br_closure(tp)
{
	var input_merge_tag = "#input_merge_tag_" + tp
	var input_merge_info = "#input_merge_info_" + tp
	var input = "#input_merge_" + tp
	var merge_list = "#input_merge_list_" + tp
	var div = '#div_res_merge_' + tp



	return function()
		{
			$(div).html('<pre>loading...</pre>')
			var base = $(input).val()
			var mlist = $(merge_list).val()

			uri = "git/merge/" + tp
			$.post(
				   uri,
	               {base_br: base, merge_list: mlist, merge_info: $(input_merge_info).val(), merge_tag: $(input_merge_tag).val()},
				   merge_br_cb_closure(div)
				   )

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
				htm = '<pre>'
				obj = obj.res
				for (var e in obj) {
					res = obj[e]
					htm += branch_show(e) + '\n'
					merge_info = res.merge
					push_info = res.push
					tag = res.tag

					htm += '[merge_info]\n' + merge_info
					htm += '\n[push_info]\n' + push_info
					if (!(tag === undefined))
						htm += '\n[tag_info]\n' + tag

					htm += '\n'

				}
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
			uri = "git/branch/" + tp
			$.post(uri, {base_br: ib, new_br: br}, create_br_cb_closure(div))

		}
}


function err_show(obj)
{

	var htm = ''
	htm = '<pre>'
	htm += '<font color="red">'
	htm += 'code:' + obj.code + '\n'
	htm += 'cmd:' + obj.cmd + '\n'
	htm += 'err:' + obj.err + '\n'
	htm += '</font>'
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
	$.get("git/stat/merge/qa", qa_merge_stat)
	$.get("git/stat/merge/dev", dev_merge_stat)
	$.get("git/stat/merge/deploy", deploy_merge_stat)
	$.get("git/stat/merge/master", master_merge_stat)
	*/

	$.get("git/stat/merge", merge_stat_all)
}

function branch_show(br)
{
	br = '['+br+']'
	return '<font color="blue">' + br + '</font>'
}

function gitweb_commit(commit_id, show)
{
	// http://172.16.10.48:8598/?p=.git;a=commit;h=ac23adab42ab40dd0afaa89f426115b85991c701
	href = "http://172.16.10.48:8598/?p=.git;a=commit;h=" + commit_id
	ac = '<a href="' + href  + '">' + commit_id + ' ' + show + '</a>'

	return ac
}

function base_br_show(br, heads)
{
	ac = gitweb_commit(heads[br][0], heads[br][2])

	return '<h4>' + branch_show(br) + ' '+ ac + '</h4>'
}

function cmp_br_show(br, heads)
{

    ac = gitweb_commit(heads[br][0], heads[br][2])

	return branch_show(br) + ' ' + ac
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
	var nomerge_master_dev_stat = obj.nomerge_master_dev_stat
	var heads = obj.heads
	var tags = obj.tags
	var old_branch = obj.old_branch
		//alert(tags)
	htm += '<h3>最新的10个tag</h3>'

	htm += '<hr/>'
	htm += '<pre>'
	for (var t in tags) {
		htm += tags[t] + '\n'
		htm += '--------------------\n'
	}
	htm += '</pre>'

		/*
	htm += '<h3>没有合并入master的release</h3>'
	htm += '<hr/>'
	for (var e in nomerge_dep_stat) {
		var cb = nomerge_dep_stat[e]
		htm += base_br_show(e, heads)
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
		htm += base_br_show(e, heads)
		htm += '<pre>'
		for (var c in cb) {
			htm += '[' + c + ']\n'
			htm += cb[c]
		}
		htm += '</pre>'

	}
		*/

	htm += '<h3>没有合并入master的develop</h3>'
	htm += '<hr/>'
	for (var e in nomerge_master_dev_stat) {
		var cb = nomerge_master_dev_stat[e]
		htm += base_br_show(e, heads)

		var isnomerge = false
		htm += '<pre>'
		for (var c in cb) {
			//htm += '[' + c + ']\n'
			htm += cmp_br_show(c, heads) + '\n'
			//htm += cb[c]
			for (var k in cb[c]) {
				htm += gitweb_commit(cb[c][k][0], cb[c][k][2]) + '\n'
			}

			isnomerge = true
		}
		if (!isnomerge) {
			htm += '没有未合并的内容'
		}
		htm += '</pre>'

	}


	htm += '<h3>develop已经并入的开发分支</h3>'
	htm += '<hr/>'
	for (var e in cmp_dev) {
		var cb = cmp_dev[e]
		htm += base_br_show(e, heads)
		htm += '<pre>'
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}




	htm += '<h3>qa/*已经并入的开发分支</h3>'
	htm += '<hr/>'
	for (var e in cmp_qa) {
		var cb = cmp_qa[e]
		htm += base_br_show(e, heads)
		htm += '<pre>'
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}




	htm += '<h3>当前开发分支合并状态</h3>'
	htm += '<hr/>'

	for (var e in dev_stat) {
		var cb = dev_stat[e]
		htm += base_br_show(e, heads)
		htm += '<pre>'
		var ismerge = false
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
			ismerge = true
		}
		if (!ismerge) {
			htm += '未合并'
		}
		htm += '</pre>'
	}


	htm += '<h3>可能已经需要删除的分支统计</h3>'
	htm += '<hr/>'
	htm += '<h3>已经合并入develop的开发(dev/*)分支，应该可以删除</h3>'
	for (var e in cmp_dev) {
		var cb = cmp_dev[e]
		htm += '<pre>'
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}
	htm += '<h3>超过7天没有提交的分支开发(dev/*)分支，应该可以删除</h3>'
	htm += '<pre>'
	for (var e in old_branch) {
		htm += cmp_br_show(old_branch[e], heads) + '\n'
	}
	htm += '</pre>'




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
