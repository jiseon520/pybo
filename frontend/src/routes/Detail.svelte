<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { link, push } from 'svelte-spa-router'
    import { is_login, username } from "../lib/store"
    import { marked } from 'marked'
    import moment from 'moment/min/moment-with-locales'
    moment.locale('ko')

    export let params = {}
    let question_id = params.question_id
    let question = {answers:[], voter:[], content: ''}
    let content = ""
    let error = {detail:[]}
    let answer_size = 10
    let answer_page = 0
    let answer_total = 0
    $: answer_total_page = Math.ceil(answer_total/answer_size)


    function get_question() {
        fastapi("get", "/api/question/detail/" + question_id, {}, (json) => {
            question = json
        })
    }
    get_question()

    function post_answer(event) {
        event.preventDefault()
        let url = "/api/answer/create/" + question_id
        let params = {
            content: content
        }
        fastapi('post', url, params, 
            (json) => {
                content = ''
                error = {detail:[]}
                get_question()
            }, 
            (err_json) => {
                error = err_json
            }
        )
    }

    function get_answer_list(_page) {
        let answer_params = {
            page: _page,
            size: answer_size,
        }
        fastapi("get", "/api/answer/list/" + question_id, answer_params, (json) => {
            question.answers = json.answer_list
            answer_page = _page
            answer_total = json.total
        })
    }

    get_answer_list(0)
    
    function delete_question(_question_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/question/delete"
            let params = {
                question_id: _question_id
            }
            fastapi('delete', url, params, 
                (json) => {
                    push('/')
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }
    
    function delete_answer(answer_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/answer/delete"
            let params = {
                answer_id: answer_id
            }
            fastapi('delete', url, params, 
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }
    
    function vote_question(_question_id) {
        let url = "/api/question/vote"
        let params = {
            question_id: _question_id
        }
        fastapi('post', url, params, 
            (json) => {
                get_question()
            },
            (err_json) => {
                error = err_json
            }
        )
    }

    function vote_answer(answer_id) {
        let url = "/api/answer/vote"
        let params = {
            answer_id: answer_id
        }
        fastapi('post', url, params, 
            (json) => {
                get_question()
            },
            (err_json) => {
                error = err_json
            }
        )
    }
</script>


<div class="container my-3">
    <!-- 질문 -->
    <h2 class="border-bottom py-2">{question.subject}</h2>
    <div class="card my-3">
        <div class="card-body">
            <div class="d-flex justify-content-end">
                <div class="mb-2">조회수 {question.views}</div>
            </div>
            <div class="card-text">
                {@html marked.parse(question.content)}
            </div>
            <div class="d-flex justify-content-end">
                {#if question.modify_date }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">수정</div>
                    <div>{moment(question.modify_date).format("M/D a h:m")}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2 text-start">
                    <div class="mb-2">{ question.user ? question.user.username : ""}</div>
                    <div class="mb-2">{moment(question.create_date).format("YY/M/D a h:m")}</div>
                </div>
            </div>            
            <div class="my-3">
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{vote_question(question.id)}"> 
                    추천
                    <span class="badge rounded-pill bg-success">{ question.voter.length }</span>
                </button>
                {#if question.user && $username === question.user.username }
                <a use:link href="/question-modify/{question.id}" 
                    class="btn btn-sm btn-outline-secondary">수정</a>
                    <button class="btn btn-sm btn-outline-secondary"
                        on:click={() => delete_question(question.id)}>삭제</button>
                {/if}
            </div>
        </div>
    </div>
    
    <button class="btn btn-secondary" on:click="{() => {
        push('/')
    }}">목록으로</button>

    <!-- 답변 목록 -->
    <h5 class="border-bottom my-3 py-2">{question.answers.length}개의 답변이 있습니다.</h5>
    {#each question.answers as answer}
    <div class="card my-3">
        <div class="card-body">
            <div class="card-text">
                {@html marked.parse(answer.content)}
            </div>
            <div class="d-flex justify-content-end">
                {#if answer.modify_date }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">수정</div>
                    <div>{moment(answer.modify_date).format("M/D a h:m")}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2 text-start">
                    <div class="mb-2">{ answer.user ? answer.user.username : ""}</div>
                    <div>{moment(answer.create_date).format("M/D a h:m")}</div>      
                </div>
            </div>
            <div class="my-3">
                <button class="btn btn-sm btn-outline-secondary" on:click="{vote_answer(answer.id)}"> 추천
                    <span class="badge rounded-pill bg-success">{ answer.voter.length }</span>
                </button>
                {#if answer.user && $username === answer.user.username }
                <a use:link href="/answer-modify/{answer.id}" 
                    class="btn btn-sm btn-outline-secondary">수정</a>                    
                <button class="btn btn-sm btn-outline-secondary"
                on:click={() => delete_answer(answer.id) }>삭제</button>
                {/if}
            </div> 
        </div>
    </div> 
    {/each}

    <!-- 답변 페이징처리 시작 -->
    <ul class="pagination justify-content-center">
        <!-- 이전페이지 -->
        <li class="page-item {answer_page <= 0 && 'disabled'}">
            <button class="page-link" on:click="{() => get_answer_list(answer_page-1)}">이전</button>
        </li>
        <!-- 페이지번호 -->
        {#each Array(answer_total_page) as _, loop_page}
        <li class="page-item {loop_page === answer_page && 'active'}">
            <button on:click="{() => answer_page = loop_page}" class="page-link">{loop_page+1}</button>
        </li>
        {/each}
        <!-- 다음페이지 -->
        <li class="page-item {answer_page >= answer_total_page-1 && 'disabled'}">
            <button class="page-link" on:click="{() => answer_page+1}">다음</button>
        </li>
    </ul>

    <!-- 답변 등록 -->
    <Error error={error} />
    <form method="post" class="my-3">
        <div class="mb-3">
            <textarea rows="10" bind:value={content} disabled={$is_login ? "" : "disabled"} class="form-control" />
        </div>
        <input type="submit" value="답변등록" class="btn btn-primary {$is_login ? '' : 'disabled'}" on:click="{post_answer}" />
    </form>
</div>
