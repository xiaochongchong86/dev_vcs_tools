function login_label()
{
	var data = $.ajax({url:"git/pricheck", type:"POST", async:false})
	var obj = eval('(' + data.responseText + ')')

	 if (obj.code != 0) {
		 $("#div_login_label").html('<a href="login">登陆</a>')

	 } else {
		 btn = '<input type="button" onclick="login_out()" value="Logout"/>'
		 $("#div_login_label").html('<a href="login">'+obj.res+'</a>' + btn)
	 }


}

function gitweb_port_cache()
{
	global_git_web_port = $.ajax({url:"gitweb/port", async:false})
	global_git_web_port = global_git_web_port.responseText
	global_git_web_port = eval('(' + global_git_web_port + ')')
	global_git_web_port = global_git_web_port[0]


}

function readydo_info()
{

    gitweb_port_cache()
	login_label()
	init_show()
}

function readydo_index()
{
	//login_label()
}


function readydo_ope()
{
	gitweb_port_cache()
	//init_show()
	login_label()
	button_click()

}

function button_click()
{
	user = $.cookie('user')
	if (!(user === undefined)) {
		$('#input_dv').val(user+'/')
		$('#input_hf').val(user+'/')
		$('#input_cqa').val(user+'/')
	}


	$("#btn_dv").click(create_br_closure('dv'))
	$("#btn_qa").click(create_br_closure('qa'))
	$("#btn_qapri").click(create_br_closure('qapri'))
	$("#btn_cqa").click(create_br_closure('cqa'))
	$("#btn_hf").click(create_br_closure('hf'))
	$("#btn_rl").click(create_br_closure('rl'))
	$("#btn_dp").click(create_br_closure('dp'))


	$("#btn_del_dv").click(delete_br_closure('dv'))
	$("#btn_del_qa").click(delete_br_closure('qa'))
	$("#btn_del_qapri").click(delete_br_closure('qapri'))
	$("#btn_del_hf").click(delete_br_closure('hf'))
	$("#btn_del_cqa").click(delete_br_closure('cqa'))


	$("#btn_merge_qa").click(merge_br_closure('qa'))
	$("#btn_merge_qapri").click(merge_br_closure('qapri'))
	$("#btn_merge_dv").click(merge_br_closure('dv'));
	$("#btn_merge_ms").click(merge_br_closure('ms'));
	$("#btn_merge_ms2").click(merge_br_closure('ms2'));
	$("#btn_merge_hf").click(merge_br_closure('hf'));



	$("#btn_check_qa").click(check_merge_br_closure('qa'))
	$("#btn_check_qapri").click(check_merge_br_closure('qapri'))
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
				var hash2br = hash_to_branch(heads)
				for (var e in check_stat) {
					var cb = check_stat[e]
					htm += base_br_show(e, heads, hash2br)

					for (var c in cb) {
						htm += cmp_br_show(c, heads, hash2br) + '\n'
						if (cb[c].length == 0) {
							htm += '没有未合并的内容\n'
						} else {
							for (var k in cb[c]) {
								htm += gitweb_commit(cb[c][k], hash2br) + '\n'
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

function delete_br_closure(tp)
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
			// use create_br_cb_closure is ok
			$.post(uri, {m:'delete', base_br: ib, new_br: br}, create_br_cb_closure(div))
		}
}



function err_show(obj)
{

	var htm = ''
	htm = '<pre>'
	htm += '<font color="red">'
	htm += 'ERROR OCCUR:\n'
	htm += 'code:' + obj.code + '\n'
	if (obj.hasOwnProperty('cmd')) {
		htm += 'cmd:' + obj.cmd + '\n'
	}

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


function gitweb_branch(branch, port)
{
	// http://172.16.10.48:8599/?p=.git;a=shortlog;h=refs/remotes/origin/dev/yangsong/scron
	href = "http://172.16.10.48:"+port+"/?p=.git;a=shortlog;h=refs/remotes/origin/"+branch
	ac = '<span class="remote"><a href="' + href  + '"><font color="red">' + branch + '</font></a></span>'

	return ac
}

function gitweb_commit(ci_info, hash2br)
{
	// http://172.16.10.48:8598/?p=.git;a=commit;h=ac23adab42ab40dd0afaa89f426115b85991c701
	// very ugly.....
	/*
	var port = $.ajax({url:"gitweb/port", async:false})
	port = port.responseText
	port = eval('(' + port + ')')
	port = port[0]
	*/
	var port = global_git_web_port
	htm = ''

	ci_id = ci_info[0]
	ci_date = ci_info[2]
	ci_author = ci_info[3]
	ci_cm = ci_info[4]

	ci_show = ci_id + ' ' + ci_date + ' ' + ci_author + ' ' + ci_cm

	href = "http://172.16.10.48:"+port+"/?p=.git;a=commit;h=" + ci_id
	ac = '<a href="' + href  + '">' + ci_show + ' ' + '</a>'
	htm += ac

	if (hash2br.hasOwnProperty(ci_id)) {
		brs = hash2br[ci_id]
		for (b in brs) {
			htm += gitweb_branch(brs[b], port)
		}
	}


	return htm
}

function base_br_show(br, heads, hash2br)
{
	ac = gitweb_commit(heads[br], hash2br)

	return '<h4>' + branch_show(br) + ' '+ ac + '</h4>'
}

function cmp_br_show(br, heads, hash2br)
{

    ac = gitweb_commit(heads[br], hash2br)

	return branch_show(br) + ' ' + ac
}

function hash_to_branch(heads)
{
	var hash2br = new Array()
	for (h in heads) {
		var hs = heads[h][0]
		if (!hash2br.hasOwnProperty(hs)) {
			hash2br[hs] = []
		}
		hash2br[hs].push(h)
	    //alert(h+' '+hs)
	}
	return hash2br

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
    var cmp_qapri = obj.cmp_qapri
    var cmp_dev = obj.cmp_dev
    var nomerge_dev_stat = obj.nomerge_dev_stat
    var nomerge_dep_stat = obj.nomerge_dep_stat
	var nomerge_master_dev_stat = obj.nomerge_master_dev_stat
	var nomerge_develop_qa_stat = obj.nomerge_develop_qa_stat
	var nomerge_master_hotfix_stat = obj.nomerge_master_hotfix_stat
	var nomerge_develop_hotfix_stat = obj.nomerge_develop_hotfix_stat
	var heads = obj.heads
	var tags = obj.tags
	var old_branch = obj.old_branch

	var hash2br = hash_to_branch(heads)


	htm += '<ul class="nav nav-tabs" id="myTab">'
	htm += '<li class="active"><a href="#tab_stat_tags" data-toggle="tab">tag信息</a></li>'
	htm += '<li><a href="#tab_stat_master_develop" data-toggle="tab">待上线</a></li>'
	htm += '<li><a href="#tab_stat_hotfix" data-toggle="tab">hotfix</a></li>'
	htm += '<li><a href="#tab_stat_qa" data-toggle="tab">qa合并统计</a></li>'

	htm += '<li><a href="#tab_stat_del" data-toggle="tab">待删除统计</a></li>'
	htm += '<li><a href="#tab_stat_dev" data-toggle="tab">开发分支合并状态</a></li>'
	htm += '</ul>'

	htm += '<div class="tab-content">'


	htm += '<div class="tab-pane active" id="tab_stat_tags">'
		//alert(tags)
	htm += '<h3>最新的10个tag</h3>'

	htm += '<hr/>'
	htm += '<pre>'
	for (var t in tags) {
		htm += tags[t] + '\n'
		htm += '--------------------\n'
	}
	htm += '</pre>'

	htm += '</div>'
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

	htm += '<div class="tab-pane" id="tab_stat_master_develop">'

	htm += '<h3>没有合并入master的develop</h3>'
	htm += '<hr/>'
	for (var e in nomerge_master_dev_stat) {
		var cb = nomerge_master_dev_stat[e]
		htm += base_br_show(e, heads, hash2br)

		var isnomerge = false
		htm += '<pre>'
		for (var c in cb) {
			//htm += '[' + c + ']\n'
			htm += cmp_br_show(c, heads, hash2br) + '\n'
			//htm += cb[c]
			for (var k in cb[c]) {
				htm += gitweb_commit(cb[c][k], hash2br) + '\n'
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
		htm += base_br_show(e, heads, hash2br)
		htm += '<pre>'
		cb.sort()
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads, hash2br) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}



	htm += '</div>'


	htm += '<div class="tab-pane" id="tab_stat_hotfix">'


	htm += '<h3>master和hotfix/*合并统计</h3>'
	htm += '<hr/>'
	for (var e in nomerge_master_hotfix_stat) {
		var cb = nomerge_master_hotfix_stat[e]
		htm += base_br_show(e, heads, hash2br)


		htm += '<pre>'
		for (var c in cb) {
			//htm += '[' + c + ']\n'
			htm += cmp_br_show(c, heads, hash2br) + '\n'
			//htm += cb[c]

			for (var k in cb[c]) {
				htm += gitweb_commit(cb[c][k], hash2br) + '\n'
			}

			if (cb[c].length == 0) {
				htm += '没有未合并的内容\n'
			}


		}

		htm += '</pre>'

	}


	htm += '<h3>develop和hotfix/*合并统计</h3>'
	htm += '<hr/>'
	for (var e in nomerge_develop_hotfix_stat) {
		var cb = nomerge_develop_hotfix_stat[e]
		htm += base_br_show(e, heads, hash2br)


		htm += '<pre>'
		for (var c in cb) {
			//htm += '[' + c + ']\n'
			htm += cmp_br_show(c, heads, hash2br) + '\n'
			//htm += cb[c]

			for (var k in cb[c]) {
				htm += gitweb_commit(cb[c][k], hash2br) + '\n'
			}

			if (cb[c].length == 0) {
				htm += '没有未合并的内容\n'
			}


		}

		htm += '</pre>'

	}


	htm += '</div>'

	htm += '<div class="tab-pane" id="tab_stat_qa">'
	htm += '<h3>develop和qa/*对比统计</h3>'
	htm += '<hr/>'
	for (var e in nomerge_develop_qa_stat) {
		var cb = nomerge_develop_qa_stat[e]
		htm += base_br_show(e, heads, hash2br)


		htm += '<pre>'
		for (var c in cb) {
			//htm += '[' + c + ']\n'
			htm += cmp_br_show(c, heads, hash2br) + '\n'
			//htm += cb[c]

			for (var k in cb[c]) {
				htm += gitweb_commit(cb[c][k], hash2br) + '\n'
			}

			if (cb[c].length == 0) {
				htm += '没有什么区别\n'
			}


		}

		htm += '</pre>'

	}





	htm += '<h3>qa/*已经并入的开发分支</h3>'
	htm += '<hr/>'
	for (var e in cmp_qa) {
		var cb = cmp_qa[e]
		htm += base_br_show(e, heads, hash2br)
		htm += '<pre>'
		cb.sort()
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads, hash2br) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}

	htm += '<h3>qapri/*已经并入的开发分支</h3>'
	htm += '<hr/>'
	for (var e in cmp_qapri) {
		var cb = cmp_qapri[e]
		htm += base_br_show(e, heads, hash2br)
		htm += '<pre>'
		cb.sort()
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads, hash2br) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}


	htm += '</div>'

	htm += '<div class="tab-pane" id="tab_stat_del">'

	htm += '<h3>可能已经需要删除的分支统计</h3>'
	htm += '<hr/>'
	htm += '<h3>已经合并入develop的开发分支(dev/*)，应该可以删除</h3>'
	for (var e in cmp_dev) {
		var cb = cmp_dev[e]
		htm += '<pre>'
		cb.sort()
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads, hash2br) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
		}
		htm += '</pre>'
	}

	htm += '<h3>没有合并入develop，但是超过7天没有提交的开发分支(dev/*)，应该可以删除</h3>'
	htm += '<pre>'
	old_branch.sort()
	for (var e in old_branch) {
		htm += cmp_br_show(old_branch[e], heads, hash2br) + '\n'
	}
	htm += '</pre>'



	htm += '</div>'

	htm += '<div class="tab-pane" id="tab_stat_dev">'


	htm += '<h3>当前开发分支合并状态</h3>'
	htm += '<hr/>'

	var dev_brs = new Array()
	for (var e in dev_stat) {
		dev_brs.push(e);
    }
	dev_brs.sort()

	for (var i in dev_brs) {
		e = dev_brs[i]
		var cb = dev_stat[e]
		htm += base_br_show(e, heads, hash2br)
		htm += '<pre>'
		var ismerge = false
		for (var i = 0; i < cb.length; i++) {
			htm += cmp_br_show(cb[i], heads, hash2br) + '\n'
			//htm += branch_show(cb[i]) + ' ' + heads[cb[i]] + '\n'
			ismerge = true
		}
		if (!ismerge) {
			htm += '未合并'
		}
		htm += '</pre>'
	}


	htm += '</div>'

	htm += '</div>'


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



function login_res(data, status)
{


	var obj = eval('(' + data + ')')

	var htm = ''
	if (obj.code != 0) {
		htm = '<font color="red">' + obj.err + '</font>'
		$("#div_login").html(htm)
	} else {

		//$("#div_login").html('<pre>ok</pre>')
		location = "/"
	}

}

function login_check(form)
{

	var u = form.user.value
	var p = form.passwd.value

	uri = "git/login"
	$.post(
		   uri,
		   {user: u, passwd: p},
		   login_res
		   )

}

function login_out()
{
	$.removeCookie('user', {path: '/'})
    $.removeCookie('passwd', {path: '/'})

	location = "/"
}