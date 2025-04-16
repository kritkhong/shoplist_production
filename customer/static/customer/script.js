const cardSearchInput = document.getElementById("searchCard")
if (cardSearchInput){
        cardSearchInput.addEventListener("keyup", function () {
                const searchValue = this.value.toUpperCase()
                const cards = document.getElementsByClassName("card")
                for(let i = 0; i < cards.length; i++){
                        const h1 = cards[i].getElementsByClassName("sale-code")[0];
                        const code = h1 ? h1.textContent.toUpperCase() : "";
                        cards[i].style.display = code.indexOf(searchValue) > -1 ? "" : "none";
                }
        
        })
}