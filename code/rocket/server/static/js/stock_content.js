const api_prefix = '/api/v0.1.0/';
let cnt = 0;
ema_l = [];
macd_l = [];
vr_l = [];

$(document).ready(function () {
    loadSymbols();
    initKChart();
    updateChart();
    updateIndicator_foo();
});


$('#addnewcommentform').submit(function (event) {
    event.preventDefault();
    let f = $('#addnewcommentform');
    $.post(api_prefix + 'stockresource/comment', f.serialize()).done(function (data) {
        $.getJSON(api_prefix + 'stockresource/comment/' + CURRENT_SYMBOL, function (result) {
            redrawComment(result);
        });
    });
    document.getElementById("addnewcommentform").reset();
    // alert(f.serialize());


});


function initKChart() {
    table = anychart.data.table();

    mapping = table.mapAs();
    mapping.addField('open', 1);
    mapping.addField('high', 2);
    mapping.addField('low', 3);
    mapping.addField('close', 4);

    ema_table = anychart.data.table();
    ema_mapping = ema_table.mapAs();
    ema_mapping.addField('value', 1);

    macd_table = anychart.data.table();
    macd_mapping = macd_table.mapAs();
    macd_mapping.addField('value', 1);

    vr_table = anychart.data.table();
    vr_mapping = vr_table.mapAs();
    vr_mapping.addField('value', 1);

    mapping2 = table.mapAs();
    mapping2.addField('value', 5);

    realtime = anychart.data.table();

    realtime_mapping = realtime.mapAs();
    realtime_mapping.addField('value', 1);

    realtime_mapping2 = realtime.mapAs();
    realtime_mapping2.addField('value', 2);


    chart = anychart.stock();
    realtime_chart = anychart.stock();


    candlestick = chart.plot(0).candlestick(mapping);

    ema = chart.plot(0).line(ema_mapping);
    ema.name('EMA');

    chart.plot(1).height('20%');

    macd = chart.plot(1).line(macd_mapping);
    macd.name('MACD');

    vr = chart.plot(1).line(vr_mapping);
    vr.name('VR');

    chart.plot(2).height('20%');
    column = chart.plot(2).column(mapping2);
    column.name('Volume');
    // candlestick.name('ACME Corp.');
    candlestick.fallingStroke('#ff0000');
    // candlestick.fallingHatchFill('#ff0000');
    candlestick.fallingFill('#ff0000');
    candlestick.risingStroke('#00ff00');
    // candlestick.risingHatchFill('#00ff00');
    candlestick.risingFill('#00ff00');

    realtime_line = realtime_chart.plot(0).line(realtime_mapping);

    realtime_p1 = realtime_chart.plot(1);
    realtime_p1.height('20%');
    realtime_column = realtime_p1.column(realtime_mapping2);
    realtime_column.name('Volume');

    chart.container('chart_container');
    chart.draw();

    realtime_chart.container('realtime_container');
    realtime_chart.draw();
}

function loadSymbols() {
    CURRENT_SYMBOL = '';
    symbols = [];
    $.getJSON(api_prefix + 'getAllSymbols', function (result) {
        $.each(result, function (idx, item) {
            symbols.push(item);
            console.log(item);
            /*$('#left_sidebar_ul').append(
                '<li class="nav-item real_time_price_nav">' +
                '<a class="nav-link" onclick=selectSymbol(\'' + item + '\')>' +
                item +
                '<span class="real_time_price" id="' + item + '_value">123</span>' +
                '</a>' +
                '</li>'
            );*/

            setTimeout(updateLeftSidebar(item), 2000);
        });
        selectSymbol(symbols[0], 'Month');
    });
}


function updateChart() {

    if ((typeof(CURRENT_SYMBOL) !== "undefined" && CURRENT_SYMBOL != null) && (typeof(CURRENT_PERIOD) !== "undefined" && CURRENT_PERIOD != null) && (typeof(table) !== "undefined" && table != null)) {
        switch (CURRENT_PERIOD) {
            case 'Year': {
                if (cnt < 300000) {
                    cnt = +2000;
                } else {
                    $.getJSON(api_prefix + 'getRecentPrice/' + CURRENT_SYMBOL + '/252', function (result) {
                        stock_data = result;
                        table.addData(stock_data);
                        // table.removeFirst(252);
                    });
                }
                setTimeout(function () {
                    updateChart();
                }, 2000);
                return;
            }
            case 'Month': {
                if (cnt < 300000) {
                    cnt = +2000;
                } else {
                    $.getJSON(api_prefix + 'getRecentPrice/' + CURRENT_SYMBOL + '/31', function (result) {
                        stock_data = result;
                        table.addData(stock_data);
                        // table.removeFirst(31);
                    });
                }
                setTimeout(function () {
                    updateChart();
                }, 2000);
                return;
            }

            case 'Day': {
                $.getJSON(api_prefix + 'getRealtimePrice/' + CURRENT_SYMBOL + '/5', function (result) {
                    stock_data = result;
                    realtime.addData(stock_data);
                    // table.removeFirst(31);
                });
                setTimeout(function () {
                    updateChart();
                }, 2000);
                return;
            }

        }
    }
    setTimeout(function () {
        updateChart();
    }, 2000);
}


function updateLeftSidebar(symbol) {
    $.getJSON(api_prefix + 'getLeastPrice/' + symbol, function (result) {
        $('#' + symbol + '_value').text(result);
        setTimeout(function () {
            updateLeftSidebar(symbol);
        }, 2000);
    })
}

function changePeriod(period) {
    selectSymbol(CURRENT_SYMBOL, period);
}

function updateIndicator_foo() {
    ema_table.addData(ema_l);
    ema_l = [];

    macd_table.addData(macd_l);
    macd_l = [];

    vr_table.addData(vr_l);
    vr_l = [];

    setTimeout(function () {
        updateIndicator_foo();
    }, 500);
}

function advice() {
    $.getJSON(api_prefix + 'getRecentPrice/' + CURRENT_SYMBOL + '/1', function (result) {
        timestamp = result[0][0];
        lastPrice = result[0][4];
        console.log('timestamp');
        $.getJSON('/api/v0.1.0/ema?symbol=' + CURRENT_SYMBOL + '&timestamp=' + timestamp, function (result) {
            ema_val = result['result']['data'];
            console.log('ema');
            $.getJSON('/api/v0.1.0/macd?symbol=' + CURRENT_SYMBOL + '&timestamp=' + timestamp, function (result) {
                macd_val = result['result']['data'];
                console.log('macd');
                $.getJSON('/api/v0.1.0/vr?symbol=' + CURRENT_SYMBOL + '&timestamp=' + timestamp, function (result) {
                    vr_val = result['result']['data'];
                    console.log('vr');
                    $('#Advice').text(getAdvice(vr_val, ema_val, macd_val));
                });
            });
        });
    });
}

function updateIndicator() {
    ema_table.remove();
    macd_table.remove();
    vr_table.remove();

    ema_l = [];
    macd_l = [];
    vr_l = [];

    $.each(stock_data, function (idx, item) {
        $.getJSON('/api/v0.1.0/ema?symbol=' + CURRENT_SYMBOL + '&timestamp=' + item[0], function (result) {
            ema_l.push([item[0], result['result']['data']]);
        });
        $.getJSON('/api/v0.1.0/macd?symbol=' + CURRENT_SYMBOL + '&timestamp=' + item[0], function (result) {
            macd_l.push([item[0], result['result']['data']]);
        });
        $.getJSON('/api/v0.1.0/vr?symbol=' + CURRENT_SYMBOL + '&timestamp=' + item[0], function (result) {
            vr_l.push([item[0], result['result']['data']]);
        });
    })
}

function selectSymbol(symbol, period = null) {
    // alert(symbol);
    CURRENT_SYMBOL = symbol;

    $('#submitSymbol').attr('value', symbol);

    $.getJSON(api_prefix + 'stockresource/comment/' + symbol, function (result) {
        redrawComment(result);
    });

    $('#stockName').text(symbol);

    if (period != null) {
        CURRENT_PERIOD = period;
        $('#timeLength').text(period);
    } else
        period = CURRENT_PERIOD;

    table.remove();
    realtime.remove();
    candlestick.name(symbol);
    realtime_line.name(symbol);

    $.getJSON('api/v0.1.0/getMax/' + symbol, function (result) {
        $('#High').text(result.toFixed(2));
    });

    $.getJSON('api/v0.1.0/getMin/' + symbol, function (result) {
        $('#Low').text(result.toFixed(2));
    });

    $.getJSON('api/v0.1.0/getAvg/' + symbol, function (result) {
        $('#Avg').text(result.toFixed(2));
    });

    $.getJSON('api/v0.1.0/getLowerAvg/' + symbol, function (result) {
        $('#Loweravg').text(result);
    });

    advice();

    switch (period) {
        case 'Year': {
            $('#realtime_container').hide();
            $("#chart_container").show();
            $.getJSON(api_prefix + 'getRecentPrice/' + symbol + '/252', function (result) {
                stock_data = result;
                table.addData(stock_data);
                updateIndicator();
            });
            break;
        }
        case 'Month': {
            $('#realtime_container').hide();
            $("#chart_container").show();
            // initKChart();
            $.getJSON(api_prefix + 'getRecentPrice/' + symbol + '/31', function (result) {
                stock_data = result;
                table.addData(stock_data);
                updateIndicator();
            });
            break;
        }

        case 'Day': {
            // initLChart();
            $("#chart_container").hide();
            $('#realtime_container').show();
            $.getJSON(api_prefix + 'getRealtimePrice/' + symbol + '/300', function (result) {
                stock_data = result;
                realtime.addData(stock_data);
            });

            break;
        }

    }

    const d = new Date();
    const timestamp1 = d.toISOString();

    $.getJSON(api_prefix + 'predict?symbol=' + symbol + '&term=long&timestamp=' + timestamp1, function (result) {
        $('#long_bayes').text(result['result']['predictor'][0]['price'].toFixed(2));
        $('#long_svr').text(result['result']['predictor'][1]['price'].toFixed(2));
        $('#long_ann').text(result['result']['predictor'][2]['price'].toFixed(2));
        $('#long_term').text(result['result']['predictPrice'].toFixed(2));
    });
    $.getJSON(api_prefix + 'predict?symbol=' + symbol + '&term=short&timestamp=' + timestamp1, function (result) {
        $('#short_bayes').text(result['result']['predictor'][0]['price'].toFixed(2));
        $('#short_svr').text(result['result']['predictor'][1]['price'].toFixed(2));
        $('#short_ann').text(result['result']['predictor'][2]['price'].toFixed(2));
        $('#short_term').text(result['result']['predictPrice'].toFixed(2));
    });


}

function foo() {
    // alert('PWN');
}

function getAdvice(VRlast, EMAlast, MACDlast) {
    const VRhigh = 160;//高于卖出
    const VRlow = 70;//低于买入
    const EMAhigh = 0;
    const EMAlow = 1;
    const MACDhigh = 0;
    const MACDlow = 0;

    let resultArray = [];
    resultArray[0] = helpAdviceVR(VRlast, VRhigh, VRlow);
    resultArray[1] = helpAdviceEMA(EMAlast, EMAhigh, EMAlow);
    resultArray[2] = helpAdviceMACD(MACDlast, MACDhigh, MACDlow);

    let buy = 0;
    let hold = 0;
    let sell = 0;
    for (let res of resultArray) {
        if (res === "1")
            buy++;
        else if (res === "0")
            hold++;
        else if (res === "-1")
            sell++;
    }

    if (buy >= 2)
        return "buy";
    else if (hold >= 2)
        return "hold";
    else if (sell >= 2)
        return "sell";
    else
        return "hold";
}

function helpAdviceVR(Test, high, low) {
    if (Test <= low)
        return "1";
    else if (Test <= high)
        return "0";
    else if (Test > high)
        return "-1";
}

function helpAdviceEMA(Test, high, low) {
    return (lastPrice >= Test) ? "1" : "-1";
}

function helpAdviceMACD(Test, high, low) {
    if (Test < low)
        return "-1";
    else if (Test <= high)
        return "0";
    else if (Test > high)
        return "1";
}

function redrawComment(newData) {
    const commentList = newData["comment"];
    document.getElementById('comments').innerHTML = "";
    for (let i = 0; i < commentList.length; i++) {
        const current = document.createElement("div");
        const h4 = document.createElement("h4");
        h4.innerText = commentList[i]["username"] + " @ " + commentList[i]["timestamp"] + " said: ";
        const p = document.createElement("p");
        p.innerText = commentList[i]["comment"];
        const hr = document.createElement("hr");
        current.appendChild(h4);
        current.appendChild(p);
        current.appendChild(hr);
        document.getElementById("comments").appendChild(current);
    }
}