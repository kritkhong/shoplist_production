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

$(".buy-form").submit(function (e){
        e.preventDefault();
        const serializedData = $(this).serialize()
        
        const formData = new FormData(this);
        url = formData.get('url')
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
                        $("#last_buy_"+product['pk']).text('last buy:' + bought_amount)
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
                                console.log(product);    
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

