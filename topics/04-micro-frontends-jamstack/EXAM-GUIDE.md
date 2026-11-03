# Tài liệu ôn vấn đáp của Toàn — Micro-Frontends và JAMstack

Đọc theo thứ tự: trang này → [ma trận yêu cầu](requirement-matrix.md) → concepts, mapping và luồng của từng project → [20 câu vấn đáp](oral-questions.md) → speaker notes. Tài liệu dùng tiếng Việt; tên API và đường dẫn giữ đúng mã.

## Phạm vi đã chốt

Theo yêu cầu của Toàn, **Micro-Frontend dùng `micro-frontend-demo` trong workspace; JAMstack dùng `ScriptHammer` trong workspace**. Blog Starter là tài liệu cũ, không phải demo chính hoặc demo bổ sung cần thực hiện. Không thay source hay chuẩn bị bài cho thành viên khác.

Nguồn chính nằm cạnh `midterm-software-architecture`, không nằm trong các bản `source/` đã copy. MFE ở commit `9a4d33596453d2d76da9d8ebb0b5c9249a0a024d`; ScriptHammer ở commit `a2dd31ae25ea30c678d990432c7e2b60b4faeda7`. Hai working tree sạch tại lần inspection ngày 03/11/2026. Xem [nguồn MFE](projects/micro-frontend-demo/SOURCE-NOTES.md) và [nguồn ScriptHammer](projects/scripthammer/SOURCE-NOTES.md).

Bạn cho biết đã chạy hai hệ thống. Lượt này chỉ đọc code, hoàn thiện tài liệu, dựng và kiểm tra **slide**, không chạy app, build app hoặc gọi backend. Vì không nhận log/ảnh của phiên demo trước, các ô runtime trong tài liệu giữ trạng thái chưa đối chiếu; không suy diễn demo thất bại hay tự đánh dấu đã kiểm chứng.

## Hai câu giải thích cốt lõi

**MFE:** MAIN ghép PRODUCTS và CART bằng cách tải container Module Federation qua HTTP lúc chạy. Tất cả component thực thi trong cùng trang. CART sở hữu trạng thái giỏ trong Zustand, nhận lệnh từ PubSub của host và phát snapshot để các UI cập nhật; localStorage giữ giỏ qua refresh. Tách bundle chưa chứng minh phát hành production độc lập.

**JAMstack:** ScriptHammer dựng trước frontend Next.js thành tệp, còn JavaScript gọi Supabase và Edge Functions cho nghiệp vụ động. Blog đi từ Markdown qua JSON rồi mới ra HTML trong build. Pages phục vụ tệp; không chạy Next.js SSR/ISR theo request. Backend, quyền dữ liệu và dữ liệu theo phiên vẫn tồn tại.

## Mở tài liệu nào khi học

| Mục tiêu | Micro-Frontend | JAMstack |
|---|---|---|
| Hiểu khái niệm và đánh đổi | [Concepts](projects/micro-frontend-demo/project-knowledge-application-implementation/01-concepts.md) | [Concepts](projects/scripthammer/project-knowledge-application-implementation/01-concepts.md) |
| Chỉ được mỗi hộp vào code | [Mapping](projects/micro-frontend-demo/project-knowledge-application-implementation/02-component-mapping.md) | [Mapping](projects/scripthammer/project-knowledge-application-implementation/02-component-mapping.md) |
| Giải thích mũi tên và trạng thái | [Luồng và sơ đồ](projects/micro-frontend-demo/project-knowledge-application-implementation/03-implementation.md) | [Luồng và sơ đồ](projects/scripthammer/project-knowledge-application-implementation/03-implementation.md) |
| Phân biệt suy luận / quan sát | [Verification](projects/micro-frontend-demo/project-knowledge-application-implementation/04-verification-and-tradeoffs.md) | [Verification](projects/scripthammer/project-knowledge-application-implementation/04-verification-and-tradeoffs.md) |
| Nhắc thao tác đã chuẩn bị | [Runbook](projects/micro-frontend-demo/demo/runbook.md) | [Runbook](projects/scripthammer/demo/runbook.md) |

## Slide và cách thuyết trình

Hai PDF trong workspace được cập nhật đúng vị trí yêu cầu: `micro-frontend-architecture/output/micro-frontend-architecture.pdf` và `jamstack-architecture/output/jamstack-architecture.pdf`. Bản có thể review qua PR nằm trong [slides](slides/README.md), gồm PDF, PPTX, notes, nguồn dựng và báo cáo QA.

Giữ mẫu **Technology Consulting by Slidesgo** lấy từ thư mục `jamstack-architecture`; SHA-256 `635dc64ea8a6cd2adea11670aa259e376fa8f3e0c5490fcf471d9d2c06776a9f`. Hai mẫu cũ có cùng hash. Dựng bằng agent-slides, giữ sơ đồ vector và phần 4+1 đã có. Xem [đối chiếu slide](slides/gap-review.md).

Task list gợi ý **6–8 slide cho cả hai chủ đề**, còn hai deck có sẵn là tài liệu đào sâu. Để ôn và trình bày ngắn, dùng 8 trang chính: MFE 2, 11, 13, 14; JAMstack 2, 10, 11, 12. Những trang còn lại phục vụ hỏi sâu và tra cứu. Đây là lộ trình rút gọn từ hai deck, không phải thêm một deck thứ ba. [Speaker notes theo lộ trình](slides/speaker-notes.md).

## Những chỗ dễ trả lời sai

1. Bản MFE ngoài repo không có Dockerfile/Compose. Cấu hình Docker/Nginx ở bản copy trong repo không được gán cho bản này.
2. `window.fsEvents` gọi callback đồng bộ trong một browser, không phải broker mạng. Replay topic `cart` trong RAM khác persistence localStorage.
3. ErrorBoundary không tạo sandbox. Remote có quyền trong cùng trang host; URL remote là ranh giới tin cậy.
4. Cart import bảng giá từ source Products lúc build; đổi remote URL không tự thay bảng giá đó.
5. ScriptHammer dùng `public/blog/*.md`, không dùng `_posts` hoặc `api.ts` của Blog Starter.
6. `generate:blog` là bước riêng; `prebuild` và `deploy.yml` đang đọc không gọi bước này. Sửa Markdown mà chưa sinh lại JSON có thể giữ nội dung cũ.
7. Có script `next start` không chứng minh hosting production dùng Node; cấu hình chính là `output: 'export'`, artifact → Pages.
8. Route guard hỗ trợ UI; quyền thật phải ở API/RLS. `NEXT_PUBLIC_*` được đưa vào frontend lúc build.

Trước buổi thi, tập giải thích một luồng bình thường, một lỗi và một đánh đổi cho mỗi chủ đề. Đối chiếu evidence từ phiên đã chạy của bạn theo runbook; tài liệu này không bổ sung yêu cầu triển khai mới.
