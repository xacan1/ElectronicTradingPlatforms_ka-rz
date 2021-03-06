const num_product_code = 1;
const num_product_name = 2;
const num_quantity = 3;
const num_unit = 4;
const num_server_price = 5;
const num_summ = 6;
const num_rate_vat = 7;
const num_owner_price_username = 8;
const num_price_step = 10;
const num_new_user_price = 11;
const num_server_user_price = 12;

window.onload = function() {
    restore_client_prices_from_JSON();
    get_current_server_summ_tender();
    ajax_get_current_tenders();
    let timer_refresh = setInterval(ajax_get_current_tenders, 2000);
    let timer_clear_flash = setTimeout(clear_flash_message, 8000);
    date_format_on_page("iso-data");
}
function decrementPrice(row_btn)
{
    let current_row = row_btn.parentNode.parentNode;
    let price_step = str_to_number(current_row.cells[num_price_step].innerHTML, 'int');
    let current_price = str_to_number(current_row.cells[num_new_user_price].childNodes[1].value, 'float');
    if (isNaN(current_price) == true || current_price == 0) {
        current_price = str_to_number(current_row.cells[num_server_price].innerHTML, 'float');
    }
    let client_price = current_price - price_step;
    current_row.cells[num_new_user_price].childNodes[1].value = client_price;
    //inp_isum(current_row.cells[10].childNodes[1]);
    save_client_prices();
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
        price_obj.product_code = table.rows[j].cells[num_product_code].innerHTML;
        price_obj.client_price = str_to_number(table.rows[j].cells[num_new_user_price].childNodes[1].value, 'float');
        client_prices.push(price_obj);
    }

    return client_prices;
}
function after_change_price()
{
    check_price_step()
    save_client_prices();
    get_current_server_summ_tender();
}
//проверим что бы изменение цены было не меньше изменения шага, в случае чего приведем цену к серверной
function check_price_step()
{
    let table = document.getElementById('table-goods');
    for (let j = 1; j < table.rows.length; j++) {
        let price_step = str_to_number(table.rows[j].cells[num_price_step].innerHTML, 'int');
        let client_price = str_to_number(table.rows[j].cells[num_new_user_price].childNodes[1].value, 'float');
        let server_price = str_to_number(table.rows[j].cells[num_server_price].innerHTML, 'float');
        if (Math.abs(server_price - client_price) < price_step || Math.abs(server_price - client_price) % price_step != 0) {
            table.rows[j].cells[num_new_user_price].childNodes[1].value = server_price;
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
        table.rows[j].cells[num_price_step].innerHTML = number_format(table.rows[j].cells[num_price_step].innerHTML, 2, ',', ' ');
        table.rows[j].cells[num_server_price].innerHTML = number_format(table.rows[j].cells[num_server_price].innerHTML, 2, ',', ' ');
        let product_code = table.rows[j].cells[num_product_code].innerHTML;
        let cell_client_price = table.rows[j].cells[num_new_user_price].childNodes[1];
        if (client_prices.length > 0 && client_prices[j-1].product_code == product_code) {
            cell_client_price.value = client_prices[j-1].client_price;
        }
        else {
            cell_client_price.value = str_to_number(table.rows[j].cells[num_server_price].innerHTML, 'float');
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
function get_user_summ_tender(username)
{
    let text_label = 'Общая сумма Вашего предложения: ';
    let summ_tender = document.getElementById('label_current_summ_tender');
    let table = document.getElementById('table-goods');
    let summ = 0;

    //проверяем есть ли текущий участник в колонке участников
    let thead = table.getElementsByTagName('thead')[0];
    let head_row = thead.rows[thead.rows.length - 1];

    if (head_row.cells[num_server_user_price].innerHTML == username) {
        for (let j = 1; j < table.rows.length; j++) {
            summ += str_to_number(table.rows[j].cells[num_server_user_price].innerHTML, 'float') * str_to_number(table.rows[j].cells[num_quantity].innerHTML, 'int');
        }

    }

    summ_tender.innerHTML = text_label + number_format(summ, 2, ',', ' ') + ' руб.';
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
        row_sum = str_to_number(table.rows[j].cells[num_server_price].innerHTML, 'float') * str_to_number(table.rows[j].cells[num_quantity].innerHTML, 'int');
        table.rows[j].cells[num_summ].innerHTML = number_format(row_sum, 2, ',', ' ');
        full_sum += row_sum;
    }

    summ_tender.innerHTML = text_label + number_format(full_sum, 2, ',', ' ') + ' руб.';
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
    let current_price, product_code;
    while (i < table_data.length) {
        row = table_data[i];
        for (let j = 1; j < table.rows.length; j++) {
            product_code = table.rows[j].cells[num_product_code].innerHTML;
            cell_server_price = table.rows[j].cells[num_server_price];
            server_price = str_to_number(cell_server_price.innerHTML)
            cell_current_price = table.rows[j].cells[num_new_user_price].childNodes[1];
            current_price = str_to_number(cell_current_price.value);

            if (row['product_code'] == product_code) {
                cell_server_price.innerHTML = number_format(row['price'], 2, ',', ' ');
                cell_owner_price_username = table.rows[j].cells[num_new_user_price];
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

    let username = table_data[0]['current_username'];//текущий юзер указан в каждой строке таблицы

    let table = document.getElementById('table-goods');
    let thead = table.getElementsByTagName('thead')[0];
    let tbody = table.getElementsByTagName('tbody')[0];
    let JSON_row, head_row, body_row;
    let cell_server_price, cell_current_price, th_cell, td_cell;
    let server_price, current_price;
    let number_cell_username = 0;// номер колонки текущего пользователя для окрашивания цен
    let number_cell_user; //число колонок с участниками(динамические колонки)
    let hide_user_row; // скрытое имя пользователя для показа пользователю
    let users = {}; //объект для записи соответствия представления участника в таблице и его id в базе
    let i = 0;
    
    while (i < table_data.length) {
        JSON_row = table_data[i];
        number_cell_user = 0;
        head_row = thead.rows[thead.rows.length - 1];

        if (JSON_row['current_access'] == 1) {
            hide_user_row = JSON_row['owner_price_username'];
        }
        else {
            hide_user_row = (JSON_row['owner_price_username'] == username)?username:'Участник ' + String(Object.keys(users).length);
        }
        
        //добавим id пользователя и представление в объект {id = 'Участник №''}
        if (!(JSON_row['owner_price_id'] in users)) {
            users[JSON_row['owner_price_id']] = hide_user_row;
        }

        //ищем колонку с текущим участником если это не админ сайта
        if (JSON_row['owner_price_access'] == 0) {
            for (let j = 1; j < head_row.cells.length; j++) {
                if (head_row.cells[j].innerHTML == users[JSON_row['owner_price_id']]) {
                    number_cell_user = j;
                    if (users[JSON_row['owner_price_id']] == username) {
                        number_cell_username = j;
                    }
                    break;
                }
            }
        }

        //если не найден участник и этот участник не админ сайта, то добавим новую колонку в конец таблицы и присвоим ей новый номер number_cell_user
        if (JSON_row['owner_price_access'] == 0 && number_cell_user == 0) {
            //добавим сразу новую колонку в конец шапки
            number_cell_user = head_row.cells.length;
            th_cell = document.createElement('th');
            head_row.appendChild(th_cell);
            th_cell.innerHTML = hide_user_row;

            //заполню новую колонку пустыми ячейками
            for (let j = 0; j < tbody.rows.length; j++) {
                body_row = tbody.rows[j];
                td_cell = document.createElement('td');
                td_cell.className = 'no-wrap digit-field';
                body_row.appendChild(td_cell);
            }
        }

        //заполню статичную часть таблицы и добавлю динамические колонки если надо
        for (let j = 0; j < tbody.rows.length; j++) {
            body_row = tbody.rows[j]; //текущая строка
            product_code = body_row.cells[num_product_code].innerHTML;
            cell_server_price = body_row.cells[num_server_price];
            server_price = str_to_number(cell_server_price.innerHTML, 'float');
            
            // если код товара совпадает, то это наша строка, заполню ее
            if (JSON_row['product_code'] == product_code) {

                //обновлю на более низкую цену если она есть
                if (JSON_row['price'] < server_price) {
                    cell_server_price.innerHTML = number_format(JSON_row['price'], 2, ',', ' ');
                    server_price = JSON_row['price'];
                }

                //если цена равна серверной, то заполню колонку владельцев цен
                if (JSON_row['price'] == server_price) {
                    body_row.cells[num_owner_price_username].innerHTML = users[JSON_row['owner_price_id']];
                }
                // теперь добавлю цены в новые колонки участников, если они есть
                if (number_cell_user > 0) {
                    body_row.cells[number_cell_user].innerHTML = number_format(JSON_row['price'], 2, ',', ' ');
                }
            }
        }
        i++;
    }
    get_user_summ_tender(username);
    coloring_table(table, username, number_cell_username);
}

//показать таймер обратного отчета до конца торгов
function show_countdown_timer(final_time)
{
    let current_date = new Date();
    let time_close_tender = document.getElementById('label_time_close');
    let time_to_close = new Date(final_time);
    time_to_close = time_to_close - current_date;

    if (time_to_close <= 0) {
        location.reload();
    }

    time_close_tender.innerHTML = 'До закрытия торгов: ' + format_time(time_to_close);
}
//преобразование миллисекунд в формат ч:м:с
function format_time(msec)
{
    let sec = Math.round(msec/1000);
    let d = sec/86400 ^ 0;
    let h = (sec-d*86400)/3600 ^ 0;
    let m = (sec-d*86400-h*3600)/60 ^ 0;
    let s = sec-d*86400-h*3600-m*60;
    return (d==0?"":d+" д. ")+(h<10?"0"+h:h)+" ч. "+(m<10?"0"+m:m)+" мин. "+(s<10?"0"+s:s)+" сек.";
}
//расскрасим цены в таблице
function coloring_table(table, username, number_cell_username)
{
    let cell_owner_price_username;
    let cell_server_price;
    let cell_column_username;

    for (let j = 1; j < table.rows.length; j++) {
        cell_server_price = table.rows[j].cells[num_server_price];
        cell_owner_price_username = table.rows[j].cells[num_owner_price_username];
        cell_column_username = table.rows[j].cells[number_cell_username];

        if (cell_owner_price_username.innerHTML == username) {
            cell_server_price.style = 'color: green; transition: color .5s linear;';
            cell_column_username.style = 'color: green; transition: color .5s linear;';
        }
        else {
            cell_server_price.style = 'color: red; transition: color .5s linear;';
            cell_column_username.style = 'color: red; transition: color .5s linear;';
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