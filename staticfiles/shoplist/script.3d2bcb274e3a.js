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

$(".plus_order").mouseenter(function(){
        $(this).siblings("input.order_adjust").val('1');
})

$(".minus_order").mouseenter(function(){
        $(this).siblings("input.order_adjust").val('-1');
})


$(".adjust-order").submit(function (e){
        e.preventDefault();
        const serializedData = $(this).serialize()
        const formData = new FormData(this);
        url = formData.get('url')
        // for (const pair of formData.entries()) {
        //         console.log(pair[0], pair[1]);
        //       }
        $.ajax({
                type: 'POST',
                url: url,
                data: serializedData,
                success: function (response) {
                        const instance = JSON.parse(response['instance'])
                        const product = instance[0]
                        // console.log(product);
                        bought_amount = product["fields"]["bought_amount"];
                        order_amount = product["fields"]["order_amount"];
                        $("#order_"+product['pk']).text(order_amount);
                        $("#order_"+product['pk']).css("color","red");
                        adjustBuyIndicator(product['pk'], bought_amount, order_amount)

                },
                error: function (response) {
                        alert(response["responseJSON"]["error"]);
                }

        })
})