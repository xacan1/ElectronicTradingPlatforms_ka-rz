window.onload = function() {
    restore_client_prices_from_JSON();
    get_current_summ_tender();
    get_current_server_summ_tender();
    ajax_get_current_tenders();
    let timer_refresh = setInterval(ajax_get_current_tenders, 2000);
    let timer_clear_flash = setTimeout(clear_flash_message, 8000);
}
function decrementPrice(row_btn)
{
    let current_row = row_btn.parentNode.parentNode;
    let price_step = parseInt(current_row.cells[4].innerHTML);
    let current_price = parseFloat(current_row.cells[10].childNodes[1].value);
    if (isNaN(current_price) == true || current_price == 0) {
        current_price = parseFloat(current_row.cells[6].innerHTML);
    }
    let client_price = current_price - price_step;
    current_row.cells[10].childNodes[1].value = client_price;
    //inp_isum(current_row.cells[10].childNodes[1]);
    save_client_prices();
    get_current_summ_tender();
}
function inp_isum(e_field)
{
    /////////////запоминание позиции курсора
    let c_p
    let ie=true
    let r
    let e_range
    if("createRange" in document) {
        c_p=e_field.selectionEnd
        ie=false
    }
    if(ie) {
        e_range=e_field.createTextRange()
        e_range.expand("character",e_field.value.length)
        r=document.selection.createRange()
        r.setEndPoint("StartToStart",e_range)
        c_p=r.text.length
        //////////// форматирование введенной строки
    }
    let txt=e_field.value
    let txt1=""
    let ii, litera
    for(let i=0;i<txt.length;i++) {
        ii=txt.length-1-i
        litera=txt.charAt(ii)
        if("0123456789".indexOf(litera)>=0) {
            txt1=litera+txt1
        }
        else {
            if(c_p>ii) c_p--
        }
    }
    /////////////сохранение готовой строки и восстановление позиции курсора
    e_field.value=txt1
    if(ie) {
        r.move("character",c_p)
        r.select()
    }
    else {
        e_field.setSelectionRange(c_p,c_p)
    }
    save_client_prices();
    get_current_summ_tender();
}
//подготовим список цен и кодов товаров для сохранения в строке JSON в случае если клиент перезагрузит страницу
function get_client_prices()
{
    // создадим объект {номер строки, код продукта, цена} и поместим эти объекты в массив
    let client_prices = [];
    let price_obj;
    let table = document.getElementById('table-goods');
    for (let j = 1; j < table.rows.length; j++) {
        price_obj = {};
        price_obj.number_row = String(j);
        price_obj.product_code = table.rows[j].cells[1].innerHTML;
        price_obj.client_price = parseFloat(table.rows[j].cells[10].childNodes[1].value);
        client_prices.push(price_obj);
    }
    return client_prices;
}
function after_change_price()
{
    check_price_step();
    save_client_prices();
    get_current_summ_tender();
    get_current_server_summ_tender();
}
//проверим что бы изменение цены было не меньше изменения шага, в случае чего приведем цену к серверной
function check_price_step()
{
    let table = document.getElementById('table-goods');
    for (let j = 1; j < table.rows.length; j++) {
        let price_step = parseInt(table.rows[j].cells[4].innerHTML);
        let client_price = parseFloat(table.rows[j].cells[10].childNodes[1].value);
        let server_price = parseFloat(table.rows[j].cells[6].innerHTML);
        if (Math.abs(server_price - client_price) < price_step) {
            table.rows[j].cells[10].childNodes[1].value = server_price;
        }
    }
}
//при первой загрузке и при полной перезагрузке страницы восстанавливает значения цен установленных клиентом из
//скрытого строкового поля tender_info_JSON
function restore_client_prices_from_JSON()
{
    let client_prices = [];
    let tender_info_JSON = document.getElementById('tender_info_JSON');
    let table = document.getElementById('table-goods');
    if (tender_info_JSON.value.length > 9) {
        client_prices = JSON.parse(tender_info_JSON.value);
    }
    for (let j = 1; j < table.rows.length; j++) {
        let product_code = table.rows[j].cells[1].innerHTML;
        let cell_client_price = table.rows[j].cells[10].childNodes[1];
        if (client_prices.length > 0 && client_prices[j-1].product_code == product_code) {
            cell_client_price.value = client_prices[j-1].client_price;
        }
        else {
            cell_client_price.value = parseFloat(table.rows[j].cells[6].innerHTML);
        }
    }
}
//сохраняет значения таблицы в скрытом строковом поле в формате JSON
function save_client_prices()
{
    let client_prices = get_client_prices();
    let tender_info_JSON = document.getElementById('tender_info_JSON');
    tender_info_JSON.value = JSON.stringify(client_prices);
}
//получает текущую сумму тендера по изменяемой колонке участника (10 колонка)
function get_current_summ_tender()
{
    let text_label = 'Общая сумма Вашего предложения: ';
    let summ_tender = document.getElementById('label_current_summ_tender');
    let table = document.getElementById('table-goods');
    let summ = 0;
    for (let j = 1; j < table.rows.length; j++) {
        summ += parseFloat(table.rows[j].cells[10].childNodes[1].value) * parseFloat(table.rows[j].cells[5].innerHTML);
    }
    summ_tender.innerHTML = text_label + number_format(summ, 2, '.', '');
}
//получает текущую сумму тендера по текущим ценам сервера (6 колонка)
function get_current_server_summ_tender()
{
    let text_label = 'Текущая сумма тендера: ';
    let summ_tender = document.getElementById('label_server_summ_tender');
    let table = document.getElementById('table-goods');
    let full_sum = 0;
    let row_sum = 0;

    for (let j = 1; j < table.rows.length; j++) {
        row_sum = parseFloat(table.rows[j].cells[6].innerHTML) * parseFloat(table.rows[j].cells[5].innerHTML);
        table.rows[j].cells[7].innerHTML = number_format(row_sum, 2, '.', '');
        full_sum += row_sum;
    }

    summ_tender.innerHTML = text_label + number_format(full_sum, 2, '.', '');
}

function get_url_post() {
    let url = window.location.href;
    let k = url.length - 1;
    let url_post = '';
    while (url[k] != '/' && k > 0) {
       url_post = url_post + url[k];
       k--;
    }
    url_post = url_post.split('').reverse().join('');
    return url_post;
}
//запрос на сервер по таймеру без перезагрузки страницы, возвращает актуальную таблицу из БД сервера
function ajax_get_current_tenders()
{
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //reload_data_table(this.response);
            update_data_table(this.response);
            get_current_server_summ_tender();
            coloring_text_row(this.response);
        }
    }
    let url_request = document.location.protocol + '//' + document.location.host + '/api/get_table_tender';
    xhttp.open('POST', url_request, true);
    xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    let params = 'url_post=' + get_url_post();
    xhttp.send(params);
}
//заполняет таблицу данными полученными от сервера при ajax запросе
//POST запрос используется что бы избежать кеширования браузером GET запроса
function reload_data_table(data)
{
    table_data = JSON.parse(data);

    if (table_data.length == 0) {
        return;
    }
    
    let table = document.getElementById('table-goods');
    let i = 0;
    let row;
    let cell_server_price;
    let cell_current_price;
    let cell_owner_price_username;
    let server_price;
    let current_price;
    while (i < table_data.length) {
        row = table_data[i];
        for (let j = 1; j < table.rows.length; j++) {
            product_code = table.rows[j].cells[1].innerHTML;
            cell_server_price = table.rows[j].cells[6];
            server_price = parseFloat(cell_server_price.innerHTML)
            cell_current_price = table.rows[j].cells[10].childNodes[1];
            current_price = parseFloat(cell_current_price.value);

            if (row['product_code'] == product_code) {
                cell_server_price.innerHTML = number_format(row['price'], 2, '.', '');
                cell_owner_price_username = table.rows[j].cells[10];
                cell_owner_price_username.innerHTML = row['owner_price_username'];
            }
        }
        i++;
    }
}
//заполняет таблицу данными полученными от сервера при ajax запросе дополняя столбцы при необходимости
//POST запрос используется что бы избежать кеширования браузером GET запроса
function update_data_table(data)
{
    table_data = JSON.parse(data);
    
    if (table_data.length == 1 && table_data[0]['id'] == 0) {
        return;
    }

    show_countdown_timer(table_data[0]['time_close']);//передаем время закрытия в миллисекундах

    let table = document.getElementById('table-goods');
    let thead = table.getElementsByTagName('thead')[0];
    let tbody = table.getElementsByTagName('tbody')[0];
    let username = table_data[0]['current_username'];//текущий юзер указан в каждой строке таблицы
    let JSON_row, head_row, body_row;
    let cell_server_price, cell_current_price, th_cell, td_cell;
    let server_price, current_price;
    let number_cell_user; //число колонок с участниками(динамические колонки)
    let hide_user_row, user_row; // скрытое и явное имя пользователя для показа по ситуации
    users = {}; //объект для записи соответствия представления участника в таблице и его id в базе
    let i = 0;
    
    while (i < table_data.length) {
        JSON_row = table_data[i];
        number_cell_user = 0;
        head_row = thead.rows[thead.rows.length - 1];
        user_row = JSON_row['owner_price_username'];

        hide_user_row = (user_row == username)?username:'Участник ' + String(Object.keys(users).length + 1);

        //добавим id пользователя и представление в объект {id = 'Участник №''}
        if (!(JSON_row['owner_price_id'] in users)) {
            users[JSON_row['owner_price_id']] = hide_user_row;
        }

        //ищем колонку с текущим участником
        for (let j = 10; j < head_row.cells.length; j++) {                
            if (head_row.cells[j].innerHTML == users[JSON_row['owner_price_id']]) {
                number_cell_user = j;
                break;
            }
        }

        //если не найден участник, то добавим новую колонку в конец таблицы и присвоим ей новый номер number_cell_user
        if (number_cell_user == 0) {
            //добавим сразу новую колонку в конец шапки
            number_cell_user = head_row.cells.length;
            th_cell = document.createElement('th');
            head_row.appendChild(th_cell);
            th_cell.innerHTML = hide_user_row;
            //заполню новую колонку пустыми ячейками
            for (let j = 0; j < tbody.rows.length; j++) {
                body_row = tbody.rows[j];
                td_cell = document.createElement('td');
                body_row.appendChild(td_cell);
            }
        }
        //заполню статичную часть таблицы и добавлю динамические колонки если надо
        for (let j = 0; j < tbody.rows.length; j++) {
            body_row = tbody.rows[j]; //текущая строка
            product_code = body_row.cells[1].innerHTML;
            cell_server_price = body_row.cells[6];
            server_price = parseFloat(cell_server_price.innerHTML);
            cell_current_price = body_row.cells[10].childNodes[1];
            current_price = parseFloat(cell_current_price.value);

            // если код товара совпадает, то это наша строка, заполню ее
            if (JSON_row['product_code'] == product_code) {
                //если цена ниже серверной, то обновлю колонку текущей ценой
                if (JSON_row['price'] < server_price) {
                    cell_server_price.innerHTML = number_format(JSON_row['price'], 2, '.', '');
                }
                // теперь добавлю цены в новые колонки участников, если они есть
                body_row.cells[number_cell_user].innerHTML = number_format(JSON_row['price'], 2, '.', '');
            }
        }
        i++;
    }
}
//показать таймер обратного отчета до конца торгов
function show_countdown_timer(final_time)
{
    let current_date = new Date();
    let time_close_tender = document.getElementById('label_time_close');
    let time_to_close = new Date(final_time);
    time_to_close = time_to_close - current_date;
    time_close_tender.innerHTML = 'До закрытия торгов: ' + format_time(time_to_close);
}
//преобразование миллисекунд в формат ч:м:с
function format_time(msec)
{
    let sec = Math.round(msec/1000);
    let h = sec/3600 ^ 0;
    let m = (sec-h*3600)/60 ^ 0;
    let s = sec-h*3600-m*60;
    return (h<10?"0"+h:h)+" ч. "+(m<10?"0"+m:m)+" мин. "+(s<10?"0"+s:s)+" сек.";
}
function coloring_text_row(data)
{
    table_data = JSON.parse(data);
    
    if (table_data.length == 0) {
        return;
    }

    let username = table_data[0]['current_username'] 
    let table = document.getElementById('table-goods');
    let cell_owner_price_username;
    let cell_server_price;
    for (let j = 1; j < table.rows.length; j++) {
        cell_server_price = table.rows[j].cells[6];
        cell_owner_price_username = table.rows[j].cells[9];
        if (cell_owner_price_username.innerHTML == username) {
            cell_server_price.style = 'color: green; transition: color .2s linear;';
        }
        else {
            cell_server_price.style = 'color: red; transition: color .2s linear;';
        }
    }
}
//по таймеру убирает надпись от flash!
function clear_flash_message()
{
    let elements = document.getElementsByClassName('flash-msg');
    for (let element of elements) {
        //element.remove();
        element.innerHTML = '...';
        //element.style = 'background-color: "#FFFFFF";';
    }
}