        window.onload = function() {
            list_products = get_list_products();
            RebuildTableFromJSON();
        }

        function get_list_products()
        {
            let list_products = [];
            let list_products_JSON = document.getElementById('list_products_JSON');
            if (list_products_JSON.value.length > 3) {
                list_products = JSON.parse(list_products_JSON.value);
            }
            return list_products;
        }

        function save_list_products(list_products)
        {
            let list_products_JSON = document.getElementById('list_products_JSON');
            list_products_JSON.value = JSON.stringify(list_products);
        }

        function addRow()
        {
            let list_products = get_list_products();

            // Считываем значения с формы
            let number_row = list_products.length;
            let product_code = document.getElementById('product_code').value;
            let product_name = document.getElementById('product_name').value;
            let unit = document.getElementById('unit').value;
            let step_price = document.getElementById('step_price').value;
            let quantity = document.getElementById('quantity').value;
            let start_price = document.getElementById('start_price').value;
            let rate_vat = document.getElementById('rate_vat').value;

            // Находим нужную таблицу
            let tbody = document.getElementById('table-goods').getElementsByTagName('tbody')[0];

            // Создаем строку таблицы и добавляем ее
            let row = document.createElement('tr');
            tbody.appendChild(row);

            // Создаем ячейки в вышесозданной строке
            // и добавляем тх
            let td0 = document.createElement('TD');
            let td1 = document.createElement('TD');
            let td2 = document.createElement('TD');
            let td3 = document.createElement('TD');
            let td4 = document.createElement('TD');
            let td5 = document.createElement('TD');
            let td6 = document.createElement('TD');
            let td7 = document.createElement('TD');
            let td8 = document.createElement('TD');//это кнопка удаления

            td0.className = 'digit-field';
            td1.className = 'string-field';
            td2.className = 'string-field';
            td3.className = 'digit-field';
            td4.className = 'digit-field';
            td5.className = 'digit-field';
            td6.className = 'digit-field';
            td7.className = 'digit-field';

            let btn_del = document.createElement('button');
            let textInBtn = document.createTextNode('-');
            btn_del.appendChild(textInBtn);
            btn_del.addEventListener('click', DeleteRow.bind(null, number_row, row));

            row.appendChild(td0);
            row.appendChild(td1);
            row.appendChild(td2);
            row.appendChild(td3);
            row.appendChild(td4);
            row.appendChild(td5);
            row.appendChild(td6);
            row.appendChild(td7);
            row.appendChild(td8);

            // Наполняем ячейки
            td0.innerHTML = number_row;
            td1.innerHTML = product_code;
            td2.innerHTML = product_name;
            td3.innerHTML = unit;
            td4.innerHTML = step_price;
            td5.innerHTML = quantity;
            td6.innerHTML = start_price;
            td7.innerHTML = rate_vat;
            td8.appendChild(btn_del);

            //готовим запрос к серверу
            let product = {};
            product.product_code = product_code;
            product.product_name = product_name;
            product.unit = unit;
            product.step_price = step_price;
            product.quantity = quantity;
            product.start_price = start_price;
            product.rate_vat = rate_vat;

            list_products.push(product);
            save_list_products(list_products);
            event.preventDefault();
        } //addRow()

        function RebuildTableFromJSON()
        {
            let list_products = get_list_products();
            let list_products_new = [];

            save_list_products(list_products_new);

            let tbody = document.getElementById('table-goods').getElementsByTagName('tbody')[0];

            while (tbody.rows.length > 0) {
                tbody.deleteRow(0);
            }

            for (index = 0; index < list_products.length; ++index) {
                let product_code = list_products[index].product_code;
                let product_name = list_products[index].product_name;
                let unit = list_products[index].unit;
                let step_price = list_products[index].step_price;
                let quantity = list_products[index].quantity;
                let start_price = list_products[index].start_price;
                if (start_price == undefined) {
                    start_price = list_products[index].price;
                }
                let rate_vat = list_products[index].rate_vat;

                let row = document.createElement('tr');
                tbody.appendChild(row);

                let td0 = document.createElement('TD');
                let td1 = document.createElement('TD');
                let td2 = document.createElement('TD');
                let td3 = document.createElement('TD');
                let td4 = document.createElement('TD');
                let td5 = document.createElement('TD');
                let td6 = document.createElement('TD');
                let td7 = document.createElement('TD');
                let td8 = document.createElement('TD');
                td0.className = 'digit-field';
                td1.className = 'string-field';
                td2.className = 'string-field';
                td3.className = 'digit-field';
                td4.className = 'digit-field';
                td5.className = 'digit-field';
                td6.className = 'digit-field';
                td7.className = 'digit-field';

                let btn_del = document.createElement('button');
                let textInBtn = document.createTextNode('-');
                btn_del.appendChild(textInBtn);
                btn_del.addEventListener('click', DeleteRow.bind(null, index, row));

                row.appendChild(td0);
                row.appendChild(td1);
                row.appendChild(td2);
                row.appendChild(td3);
                row.appendChild(td4);
                row.appendChild(td5);
                row.appendChild(td6);
                row.appendChild(td7);
                row.appendChild(td8);

                td0.innerHTML = index;
                td1.innerHTML = product_code;
                td2.innerHTML = product_name;
                td3.innerHTML = unit;
                td4.innerHTML = step_price;
                td5.innerHTML = quantity;
                td6.innerHTML = start_price;
                td7.innerHTML = rate_vat;
                td8.appendChild(btn_del);

                let product = {};
                product.product_code = product_code;
                product.product_name = product_name;
                product.unit = unit;
                product.step_price = step_price;
                product.quantity = quantity;
                product.start_price = start_price;
                product.rate_vat = rate_vat;

                list_products_new.push(product);
            }
            save_list_products(list_products_new);
            event.preventDefault();
        } //RebuildTableFromJSON()

        function DeleteRow(number_row, row)
        {
            let list_products = get_list_products();
            list_products.splice(number_row, 1);
            save_list_products(list_products);
            RebuildTableFromJSON();
        }