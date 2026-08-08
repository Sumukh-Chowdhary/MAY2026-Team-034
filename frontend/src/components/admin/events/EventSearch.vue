<template>
  <div class="search-container">

    <div class="search-wrapper">

      <span class="search-icon">
        🔍
      </span>

      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="search-input"
        type="text"
        placeholder="Search events by name or club..."
      >

    </div>

  </div>
</template>

<script setup>

defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

defineEmits([
  'update:modelValue'
])

</script>

<style scoped>

.search-container{
    width: 100%;
    max-width: 100%;
    margin: 0;
}

.search-wrapper{

    position:relative;

}

.search-icon{

    position:absolute;

    left:18px;

    top:50%;

    transform:translateY(-50%);

    font-size:18px;

    opacity:.6;

    pointer-events:none;

}

.search-input{

    width:100%;

    height:56px;

    padding:0 20px 0 52px;

    border-radius:14px;

    border:1px solid #d6dce5;

    background:#ffffff;

    font-size:16px;

    transition:all .25s ease;

}

.search-input:focus{

    outline:none;

    border-color:#2563eb;

    box-shadow:0 0 0 4px rgba(37,99,235,.12);

}

.search-input::placeholder{

    color:#94a3b8;

}

</style>