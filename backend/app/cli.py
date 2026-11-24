import argparse
import getpass
import os
import sys
from pathlib import Path

from . import auth, divisions, migrate
from .config import Settings
from .db import connect
from .telegram import TelegramClient, TelegramError
from .timeutil import utcnow


def _read_password(args):
    if args.password_stdin:
        return sys.stdin.readline().rstrip("\n")
    first = getpass.getpass("Kata sandi: ")
    if getpass.getpass("Ulangi kata sandi: ") != first:
        raise ValueError("Kata sandi tidak sama.")
    return first


def _connect(settings):
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    return connect(settings.db_path)


def _set_webhook(settings, url, transport=None):
    if not url.startswith("https://"):
        print("Gagal: URL webhook harus HTTPS.", file=sys.stderr)
        return 1
    if not settings.telegram_bot_token or not settings.telegram_webhook_secret:
        print("Gagal: JAPRI_TELEGRAM_BOT_TOKEN dan JAPRI_TELEGRAM_WEBHOOK_SECRET belum diisi.", file=sys.stderr)
        return 1
    client = TelegramClient(settings.telegram_bot_token, settings.telegram_api_base, transport=transport)
    try:
        client.set_webhook(url, settings.telegram_webhook_secret)
        client.set_commands()
    except TelegramError as exc:
        print(f"Gagal: Telegram menolak ({exc.code}).", file=sys.stderr)
        return 1
    finally:
        client.close()
    print("Webhook dan daftar perintah bot terdaftar.")
    return 0


def main(argv=None, env=None):
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("migrate", help="jalankan migrasi sampai terbaru")
    p.add_argument("--to", type=int, default=None)

    p = sub.add_parser("migrate-down", help="batalkan migrasi terakhir")
    p.add_argument("--steps", type=int, default=1)

    p = sub.add_parser("create-admin", help="buat satu-satunya akun admin")
    p.add_argument("--email", required=True)
    p.add_argument("--display-name", required=True)
    p.add_argument("--password-stdin", action="store_true", help="baca kata sandi dari stdin, bukan prompt")

    p = sub.add_parser("reset-password", help="ganti kata sandi admin dan cabut semua sesinya")
    p.add_argument("--email", required=True)
    p.add_argument("--password-stdin", action="store_true")

    p = sub.add_parser("add-division", help="tambah Divisi ke dropdown booking")
    p.add_argument("--name", required=True)
    p.add_argument("--sort-order", type=int, default=None, help="default: setelah Divisi terakhir")

    p = sub.add_parser("set-division-active", help="aktifkan atau nonaktifkan Divisi (tidak pernah dihapus)")
    p.add_argument("--name", required=True)
    p.add_argument("--active", choices=("true", "false"), required=True)

    p = sub.add_parser("set-admin-telegram", help="daftarkan akun Telegram admin untuk perintah booking di grup")
    p.add_argument("--email", required=True)
    p.add_argument("--telegram-user-id", type=int, required=True)

    p = sub.add_parser("set-webhook", help="daftarkan URL webhook dan daftar perintah bot di Telegram")
    p.add_argument("--url", required=True, help="alamat HTTPS publik, mis. https://domain/api/telegram/webhook")

    args = parser.parse_args(argv)
    settings = Settings.from_env(env if env is not None else os.environ)
    if args.command == "set-webhook":
        return _set_webhook(settings, args.url)
    conn = _connect(settings)
    try:
        if args.command == "migrate":
            print("Migrasi diterapkan:", migrate.up(conn, args.to) or "tidak ada")
        elif args.command == "migrate-down":
            print("Migrasi dibatalkan:", migrate.down(conn, args.steps) or "tidak ada")
        elif migrate.pending(conn):
            raise ValueError("Skema belum terbaru. Jalankan: python -m app.cli migrate")
        elif args.command == "add-division":
            divisions.add(conn, args.name, args.sort_order)
            print("Divisi ditambahkan.")
        elif args.command == "set-admin-telegram":
            auth.set_telegram_user(conn, args.email, args.telegram_user_id)
            print("Akun Telegram admin terdaftar.")
        elif args.command == "set-division-active":
            divisions.set_active(conn, args.name, args.active == "true")
            print("Status Divisi diubah.")
        else:
            password = _read_password(args)
            if args.command == "create-admin":
                auth.create_admin(conn, args.email, args.display_name, password, utcnow())
                print("Akun admin dibuat.")
            else:
                auth.reset_password(conn, args.email, password)
                print("Kata sandi diganti dan semua sesi dicabut.")
    except ValueError as exc:
        print(f"Gagal: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
