function deleteHouseHold(userId, houseHoldId) {
    $(function () {
        button = $("#deleteHouseHoldButton" + houseHoldId)
        // On click method for deleteHouseHold button
        button.click(function () {
            $.post({
                url: "/deleteHouseHold",
                data: {
                    userId: userId,
                    houseHoldId: houseHoldId
                },
                success: function () {
                    button.parent().remove()
                }
            })
        })
    })
}

function leaveHouseHold(userId, houseHoldId) {
    $(function () {
        button = $("#leaveHouseHoldButton" + houseHoldId)
        // On click method for leaveHouseHold button
        button.click(function () {
            $.post({
                url: "/leaveHouseHold",
                data: {
                    userId: userId,
                    houseHoldId: houseHoldId
                },
                success: function () {
                    button.parent().remove()
                }
            })
        })
    })
}