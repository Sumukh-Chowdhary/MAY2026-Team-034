<script setup>

defineProps({
  modelValue: {
    type: String,
    default: 'all'
  },
  counts: {
    type: Object,
    default: () => ({ all: 0, live: 0, completed: 0 })
  }
})

defineEmits(['update:modelValue'])

</script>

<template>
  <div class="status-toggle">

    <button
      class="toggle-option"
      :class="{active:modelValue==='all'}"
      @click="$emit('update:modelValue','all')"
    >
      All
      <span class="count">{{ counts.all }}</span>
    </button>

    <button
      class="toggle-option"
      :class="{active:modelValue==='live'}"
      @click="$emit('update:modelValue','live')"
    >
      Live
      <span class="count">{{ counts.live }}</span>
    </button>

    <button
      class="toggle-option"
      :class="{active:modelValue==='completed'}"
      @click="$emit('update:modelValue','completed')"
    >
      Completed
      <span class="count">{{ counts.completed }}</span>
    </button>

  </div>
</template>

<style scoped>

.status-toggle{
    display:inline-flex;
    background:white;
    border:1px solid #D1D5DB;
    border-radius:14px;
    padding:5px;
    gap:4px;
    margin:0;
}

.toggle-option{

    border:none;

    background:transparent;

    padding:12px 24px;

    border-radius:10px;

    font-weight:600;

    color:#475569;

    display:flex;

    align-items:center;

    gap:10px;

    transition:all .25s ease;

}

.toggle-option:hover{

    background:#EFF6FF;

}

.toggle-option.active{

    background:#2563EB;

    color:white;

}

.count{

    width:24px;

    height:24px;

    border-radius:50%;

    display:flex;

    justify-content:center;

    align-items:center;

    background:rgba(37,99,235,.1);

    color:#2563EB;

    font-size:.75rem;

    font-weight:700;

}

.toggle-option.active .count{

    background:white;

    color:#2563EB;

}

</style>