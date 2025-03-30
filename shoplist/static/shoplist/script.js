document.getElementById("sale_date").onchange = function() {
        window.location.href = this.value;        
};

const adjustBuyIndicator = function(pk, bought_amount, order_amount){
        remain = order_amount - bought_amount;
        if(remain > 0){
                $("#buy_indicator_"+pk).html('<div class="bg-primary-subtle text-primary-emphasis p-3"><p>buy:</p><p class="display-1">'+ remain+'</p></div>');    
                $("#exceed_warn_"+pk).text('');
        } else if (remain < 0){
                $("#buy_indicator_"+pk).html('<div class="text-bg-danger"><p class="display-2">EXCEED</p></div>');
                $("#exceed_warn_"+pk).text('⁉️ exceed ');
                $("#amount_"+pk).css("color","red");
        } else if (bought_amount > 0){
                $("#buy_indicator_"+pk).html('<div class="text-bg-success"><p class="display-1">DONE</p></div>');
                $("#exceed_warn_"+pk).text('');
        } else {
                $("#buy_indicator_"+pk).html('');
                $("#exceed_warn_"+pk).text('');
        }

}

buyAdjBtns = document.getElementsByClassName("buy-adjust")
for (let i = 0; i < buyAdjBtns.length; i++){
        buyAdjBtns[i].addEventListener("click", function() {
                const productId = this.getAttribute("product-id");
                const adjValue = parseInt(this.getAttribute("value"));
                buyInput = document.getElementById("buy_input_"+productId)
                buyInputVal = buyInput.value
                if(!buyInputVal){
                        buyInputVal = 0
                }
                newVal = parseInt(buyInputVal) + adjValue
                buyInput.value = newVal
        })
}



cardSearchInput = document.getElementById("searchCard")
if (cardSearchInput){
        cardSearchInput.addEventListener("keyup", function () {
                searchValue = this.value.toUpperCase()
                cards = document.getElementsByClassName("card")
                for(let i = 0; i < cards.length; i++){
                        h1 = cards[i].getElementsByClassName("sale-code")[0]; 
                        if (h1) {
                                let code = h1.textContent;
                                if (code.toUpperCase().indexOf(searchValue)>-1){
                                        cards[i].style.display = "";
                                } else {
                                        cards[i].style.display = "none";
                                }
                        }
                }
        
        })
}



tableSearchInput = document.getElementById("searchTable")
if (tableSearchInput) {
        tableSearchInput.addEventListener("keyup", function () {
                searchValue = this.value.toUpperCase()
                tbody = document.getElementsByTagName("tbody")[0]
                tr = tbody.getElementsByTagName("tr")
                for(let i = 0; i < tr.length; i++){
                        th = tr[i].getElementsByTagName("th")[0];
                        if (th) {
                                let code = th.textContent;
                                if (code.toUpperCase().indexOf(searchValue)>-1){
                                        tr[i].style.display = "";
                                } else {
                                        tr[i].style.display = "none";
                                }
                        }
                }
        
        })
}




$(".buy-form").submit(function (e){
        e.preventDefault();
        const serializedData = $(this).serialize()
        
        const formData = new FormData(this);
        url = formData.get('url')
        buy_value = formData.get('buy_amount')
        $.ajax({
                type: 'POST',
                url: url,
                data: serializedData,
                success: function (response) {
                        const instance = JSON.parse(response['instance'])
                        const product = instance[0]
                        // change bought_amount to new value 
                        // scroll to next post
                        bought_amount = product["fields"]["bought_amount"];
                        order_amount = product["fields"]["order_amount"];
                        adjustBuyIndicator(product['pk'],bought_amount,order_amount)
                        $("#buy_input_"+product['pk']).val('');
                        $("#amount_"+product['pk']).text(bought_amount)
                        $("#last_buy_"+product['pk']).text('last buy:' + buy_value)
                        if (bought_amount <= order_amount) {
                                window.scrollBy({
                                        top: $("#field_"+product['pk']).height()+18,
                                        behavior: "smooth",
                                      });
                        }

                        



                },
                error: function (response) {
                        alert(response["responseJSON"]["error"]);
                }

        })
})

// $(".plus_order").mouseenter(function(){
//         $(this).siblings("input.order_adjust").val('1');
// })

// $(".minus_order").mouseenter(function(){
//         $(this).siblings("input.order_adjust").val('-1');
// })


// $(".adjust-order").submit(function (e){
//         e.preventDefault();
//         const serializedData = $(this).serialize()
//         const formData = new FormData(this);
//         url = formData.get('url')
//         for (const pair of formData.entries()) {
//                 console.log(pair[0], pair[1]);
//               }
//         $.ajax({
//                 type: 'POST',
//                 url: url,
//                 data: serializedData,
//                 success: function (response) {
//                         const instance = JSON.parse(response['instance'])
//                         const product = instance[0]
//                         // console.log(product);
//                         bought_amount = product["fields"]["bought_amount"];
//                         order_amount = product["fields"]["order_amount"];
//                         $("#order_"+product['pk']).text(order_amount);
//                         $("#order_"+product['pk']).css("color","red");
//                         adjustBuyIndicator(product['pk'], bought_amount, order_amount)

//                 },
//                 error: function (response) {
//                         alert(response["responseJSON"]["error"]);
//                 }

//         })
// })

function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }

notes = document.getElementsByClassName("note")
for (let i = 0; i < notes.length; i++){
        notes[i].addEventListener("focusout", function(){
                console.log("focusout");
                const formData = new FormData();
                const productId = this.getAttribute("product-id");
                const noteText = this.value;
                formData.append("product_id", productId);
                formData.append("note", noteText);
                const url = this.getAttribute("url");
                fetch(url,{
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                                "x-requested-with": "XMLHttpRequest",
                                "X-CSRFToken": getCookie("csrftoken"),
                        },
                        body: formData
                })
                .then(response => response.json())
                .then(function(data) {
                        if (data.hasOwnProperty("error")){
                                alert(data['error'])
                        }
                      })


        })
}

orderAdjBtns = document.getElementsByClassName("adjust-order-btn")
for (let i = 0; i < orderAdjBtns.length; i++ ){
        orderAdjBtns[i].addEventListener("click", function () {
                const formData = new FormData();
                // console.log(this);
                const productId = this.getAttribute("product-id");
                const value = this.getAttribute("value");
                formData.append("product_id", productId);
                formData.append("order_adjust", value);
                const url = this.getAttribute("url");
                const serializedData = new URLSearchParams(formData);
                fetch(url, {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                          "x-requested-with": "XMLHttpRequest",
                          "X-CSRFToken": getCookie("csrftoken"),
                        },
                        body: formData
                      })
                      .then(response => response.json())
                      .then(function(data) {
                        if (data.hasOwnProperty("instance")){
                                const instance = JSON.parse(data['instance']);
                                const product = instance[0];
                                boughtAmount = product["fields"]["bought_amount"];
                                orderAmount = product["fields"]["order_amount"];
                                orderCountObj = document.getElementById("order_"+product['pk'])
                                orderCountObj.textContent = orderAmount;
                                orderCountObj.style.color = "red";
                                adjustBuyIndicator(product['pk'], boughtAmount, orderAmount)

                        } else {
                                alert(data['error'])
                        }
                                


                      })


        })
}

