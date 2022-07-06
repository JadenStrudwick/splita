function deleteBill(userId, houseHoldId, billId) {
    $(function () {
        // On click method for deleteBill button
        $("#deleteBillButton" + billId).click(function () {
            $.post({
                url: "/deleteBill",
                data: {
                    userId: userId,
                    houseHoldId: houseHoldId,
                    billId: billId
                },
                success: function () {
                    $("#bill" + billId).remove()
                }
            })
        })
    })
}

function payBill(userName, userId, houseHoldId, billId) {
    $(function () {
        // On click method for payBill button
        $("#payBillButton" + billId).click(function () {
            $.post({
                url: "/payBill",
                data: {
                    userId: userId,
                    houseHoldId: houseHoldId,
                    billId: billId
                },
                success: function () {
                    $("#" + userId + billId).html(userName + " has paid")
                    $("#" + userId + billId).css("text-decoration", "line-through")
                }
            })
        })
    })
}