<div id="delete_chat_modal" class="fixed z-20 inset-0 overflow-y-auto bg-gray-800 bg-opacity-75 hidden">
    <div class="flex items-center justify-center min-h-screen">
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg max-w-md w-full">
            <button type="button"
                class="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ml-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white"
                data-modal-hide="delete_chat_modal">
                <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
                    viewBox="0 0 14 14">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"></path>
                </svg>
                <span class="sr-only">Close modal</span>
            </button>
            <div class="p-6 text-center">
                <svg class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M10 11V6m0 8h.01M19 10a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"></path>
                </svg>
                <h3
                    class="mb-5 text-lg font-normal text-gray-500 flex-col dark:text-gray-400 overflow-hidden flex justify-center items-center">
                    <span>您確定要刪除聊天室 </span>
                    <span class="truncate-text overflow-hidden overflow-ellipsis inline-block max-w-[200px] text-lg"
                        style="text-wrap:nowrap">&lt;hi&gt;</span>
                </h3>
                <input name="id" type="hidden" value="">
                <button onclick="deleteRoom($(this).prev().val())"
                    class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 dark:focus:ring-red-800 font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center mr-2">
                    刪除
                </button>
                <button onclick="$('#delete_chat_modal').addClass('hidden')" type="button"
                    class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600">取消</button>
            </div>
        </div>
    </div>
</div>
<script>
    function deleteRoom(id) {
        $('#delete_chat_modal').addClass('hidden');
        client.deleteRoom(id)
            .then(response => {
                if (window.location.pathname.includes(`/room/${id}`)) {
                    window.location.href = '/room';
                } else {
                    client.listRooms()
                        .then(rooms => {
                            generateDropdown(botData);
                            refreshChatRoomList(groupByTime(rooms.result),
                                {{ request()->user()->hasPerm('Room_delete_chatroom') }},
                                botData);
                        })
                        .catch(error => console.error('Error:', error));
                }
            })
            .catch(error => console.error('Error during room deletion:', error));
    }
</script>
