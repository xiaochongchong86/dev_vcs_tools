function readydo()
{
	init_show()

	button_click()

}

function button_click()
{
	$("#btn1").click(
		function(){
		alert("Text: " + $("#text1").val());
	});

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

    var dev_stat = obj.dev_stat
    var cmp_qa = obj.cmp_qa
    var cmp_dev = obj.cmp_dev
    var nomerge_dev_stat = obj.nomerge_dev_stat
    var nomerge_dep_stat = obj.nomerge_dep_stat

	htm += '<h3>没有合并入master的deploy</h3>'
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


	htm += '<h3>没有合并入deploy的develop</h3>'
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
		for (var i = 0; i < cb.length; i++) {
			htm += '[' + cb[i] + ']'
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
