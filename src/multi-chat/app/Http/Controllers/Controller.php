<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Foundation\Validation\ValidatesRequests;
use Illuminate\Routing\Controller as BaseController;

/**
 * @OA\Info(
 *     title="Kuwa API",
 *     version="1.0.0",
 *     description="API definition for KuwaClient service"
 * )
 *
 * @OA\SecurityScheme(
 *     securityScheme="bearerAuth",
 *     type="http",
 *     scheme="bearer",
 *     bearerFormat="JWT"
 * )    
 * @OA\Schema(
 *     schema="BaseModel",
 *     type="object",
 *     @OA\Property(property="name", type="string"),
 *     @OA\Property(property="access_code", type="string"),
 *     @OA\Property(property="description", type="string"),
 *     @OA\Property(property="other_field", type="string")
 * )
 * @OA\Schema(
 *     schema="CreateRoomRequest",
 *     type="object",
 *     @OA\Property(
 *         property="llm",
 *         type="array",
 *         @OA\Items(type="integer")
 *     )
 * )
 * @OA\Schema(
 *     schema="CreateUserRequest",
 *     type="object",
 *     @OA\Property(
 *         property="users",
 *         type="array",
 *         @OA\Items(
 *             @OA\Property(property="name", type="string"),
 *             @OA\Property(property="email", type="string"),
 *             @OA\Property(property="password", type="string"),
 *             @OA\Property(property="group", type="string"),
 *             @OA\Property(property="detail", type="string"),
 *             @OA\Property(property="require_change_password", type="boolean")
 *         )
 *     )
 * )
 * @OA\Schema(
 *     schema="CreateBotRequest",
 *     type="object",
 *     @OA\Property(property="llm_access_code", type="string"),
 *     @OA\Property(property="bot_name", type="string"),
 *     @OA\Property(property="visibility", type="integer")
 * )
 */


class Controller extends BaseController
{
    use AuthorizesRequests, ValidatesRequests;
}
