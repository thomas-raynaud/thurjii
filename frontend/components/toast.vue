<template>
    <div class="toast-container position-fixed top-0 end-0 p-3">
        <div ref="toast-element" class="toast align-items-center" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    {{ message }}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, useTemplateRef, onMounted } from 'vue'

    const message = ref("")
    const toast_element = useTemplateRef("toast-element")
    let toast

    onMounted(() => {
        toast = bootstrap.Toast.getOrCreateInstance(toast_element.value)
    })

    const display_toast = (in_message) => {
        message.value = in_message
        toast.show()
    }

    defineExpose({
        display_toast
    })
</script>
